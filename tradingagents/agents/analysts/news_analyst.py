from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_news_analyst(llm, toolkit):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            # Use Google News for comprehensive coverage
            tools = [
                toolkit.get_google_news,         # ✅ WORKING: Real Google news API
            ]
        else:
            # When offline, skip news analysis rather than use fake LLM news
            tools = []

        system_message = (
            f"You are a financial news analyst specializing in {ticker} and market-moving events. Your task is to gather and analyze the most recent, high-impact news that could affect {ticker}'s stock price and trading decisions. Focus on actionable intelligence rather than general market commentary."
            + """
            **WORKFLOW:**
            1. **First**: If you haven't received news data yet, call get_google_news tool to fetch comprehensive news coverage
            2. **Second**: AFTER receiving the tool results with news articles, you MUST immediately write a comprehensive analysis report (do NOT just describe what function to call - the data is already provided!)

            **CRITICAL**: When you see news data in the tool results (indicated by "📊 News Coverage Statistics" and multiple news articles), you are in step 2 - write your analysis report immediately based on that data. Do NOT suggest calling functions again.

            **REPORT STRUCTURE:**
            Your report MUST start with a brief summary section that includes:
            - Total number of news articles retrieved
            - Number of different news sources
            - Top news sources (e.g., "Reuters (5), Bloomberg (3), Yahoo Finance (2)")
            - Date range covered

            Example opening:
            "Analyzed 18 news articles from 8 different sources including Reuters (5), Bloomberg (3), and Yahoo Finance (2) covering the period from [date] to [date]."

            CRITICAL REQUIREMENTS:

            **MANDATORY MINIMUM**: You MUST analyze EXACTLY 8-10 news items with DETAILED, FACT-RICH content in your report (minimum 8, maximum 10). Do NOT stop after 3-6 items. Number each news item clearly (NEWS #1, NEWS #2, ..., NEWS #8) to track your progress.

            **QUALITY OVER QUANTITY**: Each news item MUST contain specific numbers, data points, and facts that other analysts can reference for their cross-analysis. Vague summaries are NOT acceptable.

            1. **NEWS SELECTION**: From all available news (30-40 articles), intelligently select EXACTLY 8-10 MOST IMPORTANT news items based on:
               - Timeliness (most recent news gets priority)
               - Market impact potential (explosive/breaking news)
               - Relevance to trading decisions
               - Significance for the target company/ticker

            2. **LANGUAGE**: Write EVERYTHING in English only. No Chinese text.

            3. **DETAILED FORMAT FOR EACH NEWS ITEM** (Include specific data and facts - these details are CRITICAL for other analysts to reference):
               - ### NEWS #X: [Full Headline] (source: Source Name, Date)
               - **Summary**: 3-4 sentences with SPECIFIC DETAILS:
                 * What exactly happened (include numbers, percentages, dollar amounts, dates)
                 * Key data points (revenue, earnings, growth rates, market share, etc.)
                 * Who said what (direct quotes if available)
                 * Context and background
               - **Market Impact**: 2-3 sentences analyzing:
                 * Estimated stock price effect (+/-X%)
                 * Which metrics/factors this affects (e.g., P/E, revenue growth, cash flow)
                 * Short-term vs long-term implications
               - **URL**: [Full URL - REQUIRED]

               EXAMPLE:
               ### NEWS #1: Apple Reports Record Q3 iPhone Sales Beating Expectations by 15% (source: Reuters, Oct 15, 2025)
               **Summary**: Apple Inc. announced Q3 2025 iPhone sales of $45.2 billion, surpassing analyst consensus estimates of $39.3 billion by 15%. CEO Tim Cook stated "iPhone demand remains robust across all regions, with particularly strong performance in emerging markets where sales grew 28% YoY." The company sold 58.3 million iPhone units in the quarter, driven by the new iPhone 16 Pro Max which accounted for 35% of total sales. This marks the highest quarterly iPhone revenue in company history, despite ongoing macroeconomic headwinds in key markets.
               **Market Impact**: Likely +3-5% short-term price increase as investors react to revenue growth potential. This strong iPhone performance should improve revenue growth metrics and could support a higher P/E ratio multiple. The 28% emerging market growth suggests sustainable long-term expansion potential, which should positively impact forward earnings estimates and valuation models.
               **URL**: https://www.reuters.com/business/apple-record-sales-2025

            4. **OVERALL NEWS SENTIMENT ANALYSIS** (ONLY AFTER completing 10-12 news items): After presenting individual news items, provide a comprehensive synthesis section:
               - **Overall Market Sentiment**: Aggregate sentiment (bullish/bearish/neutral) with percentage distribution
               - **Key Themes**: Top 3-5 recurring themes across all news (e.g., "AI growth", "regulatory concerns", "earnings beats")
               - **Net Impact Assessment**: Combined effect on stock price considering all news (+/-X% estimated)
               - **Trading Implications**: Specific actionable insights for traders (buy/hold/sell signals, key price levels to watch)
               - **Risk Factors**: Main downside risks identified across news coverage

            5. **SUMMARY TABLE**: End with a table showing:
               | News Category | Count | Sentiment | Estimated Impact |
               |--------------|-------|-----------|------------------|
               | Earnings     | X     | Positive  | +Y%              |
               | Product      | X     | Mixed     | +/-Y%            |
               [etc...]

            **IMPORTANT**: DO NOT just list news headlines with links. Each news item MUST have substantive analysis explaining WHY it matters and HOW it affects trading decisions.

            IGNORE routine/repetitive news like minor institutional holdings changes. Focus on BREAKING NEWS, EARNINGS, PRODUCT LAUNCHES, REGULATORY CHANGES, ANALYST UPGRADES/DOWNGRADES, and MAJOR MARKET EVENTS.

            **CRITICAL**: Every news item MUST include a **URL** line. If you cannot find the actual URL, use a relevant search URL like https://www.google.com/search?q=[headline] but ALWAYS include a URL line.

            **BEFORE FINISHING - SELF-CHECK**:
            Count the news items you've written. Have you completed at LEAST 8 DETAILED items with specific data (NEWS #1 through NEWS #8)?
            - If YES (8+ items with facts/numbers): Proceed to write the Overall News Sentiment Analysis section
            - If NO (less than 8, or items lack specific data): STOP and add more detailed news items until you reach NEWS #8

            This is NOT OPTIONAL - you MUST have 8-10 DETAILED, FACT-RICH news items before writing the summary section."""
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

        # Add retry logic for WatsonX connection issues
        max_retries = 3
        retry_count = 0
        result = None

        while retry_count < max_retries:
            try:
                result = chain.invoke(state["messages"])
                break  # Success, exit retry loop
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                if "Server disconnected" in error_msg or "502 Bad Gateway" in error_msg or "RemoteProtocolError" in error_msg:
                    if retry_count < max_retries:
                        print(f"[RETRY] WatsonX connection error (attempt {retry_count}/{max_retries}), retrying in 3 seconds...", flush=True)
                        time.sleep(3)
                    else:
                        print(f"[ERROR] WatsonX connection failed after {max_retries} attempts", flush=True)
                        raise
                else:
                    # Other errors, don't retry
                    raise

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "news_report": report,
        }

    return news_analyst_node
