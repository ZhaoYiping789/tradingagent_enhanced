from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_social_media_analyst(llm, toolkit):
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = []  # Reddit tools not working, disable for now
        else:
            tools = []  # No working social media tools available

        system_message = (
            "You are a detailed social media and news sentiment analyst. Your task is to provide a comprehensive report in ENGLISH ONLY that includes:"
            "\n\n**CRITICAL REQUIREMENTS:**"
            "\n1. **LANGUAGE**: Write EVERYTHING in English only. No Chinese text."
            "\n2. **FOCUS**: Select only the MOST SIGNIFICANT sentiment indicators and social media trends"
            "\n3. **SPECIFIC CONTENT REQUIRED:**"
            "\n   - Top 3-5 most impactful news headlines with sources and dates"
            "\n   - Key direct quotes from influential social media posts or news articles"
            "\n4. **Source Links**: When possible, mention specific news sources (e.g., Reuters, Bloomberg, CNBC, etc.)"
            "\n4. **Sentiment Breakdown**: Provide numerical sentiment scores (positive/negative/neutral percentages)"
            "\n5. **Social Media Trends**: Mention specific platforms (Twitter/X, Reddit, LinkedIn) and trending topics"
            "\n6. **Key Influencer Opinions**: Reference specific analyst or influencer comments"
            "\n7. **Volume Analysis**: Comment on the volume of mentions/discussions"
            "\n8. **Time-based Analysis**: Break down sentiment changes over the past week"
            "\n\n**REPORT STRUCTURE:**"
            "\n- Executive Summary with key sentiment metrics"
            "\n- Detailed News Analysis (with specific headlines and sources)"
            "\n- Social Media Sentiment Breakdown"
            "\n- Key Quotes and Influential Opinions"
            "\n- Sentiment Timeline (daily breakdown if possible)"
            "\n- Trading Implications"
            "\n- Detailed Summary Table with sources and sentiment scores"
            "\n\nBe specific, detailed, and provide concrete examples. Include actual content rather than general statements.",
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
                    "For your reference, the current date is {current_date}. The current company we want to analyze is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        # Handle case when no tools are available
        if not tools:
            report = f"Social media analysis unavailable due to API limitations. Recommend manual review of social platforms for {ticker} sentiment around {current_date}."
            return {
                "messages": [],
                "sentiment_report": report,
            }

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return social_media_analyst_node
