from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_news_analyst(llm, toolkit):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            # Use only working real-time news APIs
            tools = [
                toolkit.get_google_news,         # ✅ WORKING: Real Google news API
            ]
        else:
            # When offline, skip news analysis rather than use fake LLM news
            tools = []

        system_message = (
            f"You are a financial news analyst specializing in {ticker} and market-moving events. Your task is to gather and analyze the most recent, high-impact news that could affect {ticker}'s stock price and trading decisions. Focus on actionable intelligence rather than general market commentary."
            + """ CRITICAL REQUIREMENTS:
            1. **NEWS SELECTION**: From all available news, intelligently select only the 5-10 MOST IMPORTANT news items based on:
               - Timeliness (most recent news gets priority)
               - Market impact potential (explosive/breaking news)
               - Relevance to trading decisions
               - Significance for the target company/ticker
            
            2. **LANGUAGE**: Write EVERYTHING in English only. No Chinese text.
            
            3. **MANDATORY FORMAT**: For each selected news item, you MUST include:
               - ### [Headline] (source: Source Name)
               - Brief but insightful summary (2-3 sentences)
               - **URL**: [Full clickable URL - REQUIRED]
               - **Impact Assessment**: High/Medium/Low
               
               EXAMPLE FORMAT:
               ### Apple Reports Record iPhone Sales (source: Reuters)
               Apple Inc. announced record-breaking iPhone sales for Q3 2025...
               **URL**: https://www.reuters.com/business/apple-record-sales-2025
               **Impact Assessment**: High
            
            4. **DETAILED IMPACT ANALYSIS**: For each news item, provide specific analysis:
               - **Price Impact**: How this could affect stock price (specific % estimates)
               - **Volume Impact**: Expected trading volume changes
               - **Sector Impact**: Effects on related stocks/sector
               - **Timeline**: When the impact is expected to materialize
               - **Risk Factors**: What could go wrong with this news
            
            5. **QUANTITATIVE ASSESSMENT**: Replace generic "High/Medium/Low" with:
               - **Estimated Price Impact**: +/-X% over Y timeframe
               - **Probability of Impact**: X% chance of occurring
               - **Risk-Adjusted Impact**: Expected value calculation
            
            6. **TABLE**: End with a comprehensive table including quantitative impact metrics
            
            IGNORE routine/repetitive news like minor institutional holdings changes. Focus on BREAKING NEWS, EARNINGS, PRODUCT LAUNCHES, REGULATORY CHANGES, ANALYST UPGRADES/DOWNGRADES, and MAJOR MARKET EVENTS.
            
            **CRITICAL**: Every news item MUST include a **URL** line. If you cannot find the actual URL, use a relevant search URL like https://www.google.com/search?q=[headline] but ALWAYS include a URL line."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. We are looking at the company {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        # Handle case when no tools are available
        if not tools:
            report = f"Real-time news analysis unavailable. Recommend checking financial news sources manually for {ticker} updates around {current_date}."
            return {
                "messages": [],
                "news_report": report,
            }

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "news_report": report,
        }

    return news_analyst_node
