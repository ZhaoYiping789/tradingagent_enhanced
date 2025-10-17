from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_market_analyst(llm, toolkit):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_YFin_data_online,
                toolkit.get_stockstats_indicators_report_online,
            ]
        else:
            tools = [
                toolkit.get_YFin_data,
                toolkit.get_stockstats_indicators_report,
            ]

        system_message = (
            """You are a technical analyst specializing in comprehensive market analysis. Your report MUST include BOTH detailed text analysis AND data tables.

**REQUIRED INDICATORS (Call ALL 12):**
Moving Averages: close_50_sma, close_200_sma, close_10_ema
MACD: macd, macds, macdh (ALL THREE)
Momentum: rsi
Volatility: boll, boll_ub, boll_lb, atr
Volume: vwma

**WORKFLOW:**
1. First call get_YFin_data to get price data
2. Then call get_stockstats_indicators_report for each of the 12 indicators above
3. AFTER you receive all indicator values, write your comprehensive analysis report

**REPORT STRUCTURE (CRITICAL - Include ALL sections with detailed text analysis):**

## Technical Overview
Write 2-3 sentences summarizing the overall technical picture and current market phase.

## Trend Analysis (Moving Averages)
- Present 50 SMA, 200 SMA, 10 EMA values
- Write 3-4 sentences analyzing:
  * Current price position relative to moving averages
  * Golden cross / death cross signals
  * Support and resistance levels
  * Short-term vs long-term trend alignment

## Momentum Analysis (MACD & RSI)
- Present MACD, MACD Signal, MACD Histogram, RSI values
- Write 3-4 sentences analyzing:
  * MACD crossover signals and histogram direction
  * RSI overbought/oversold conditions (>70 overbought, <30 oversold)
  * Divergence patterns if present
  * Momentum strength and direction

## Volatility Analysis (Bollinger Bands & ATR)
- Present Bollinger Upper, Middle, Lower bands and ATR value
- Write 3-4 sentences analyzing:
  * Current price position within bands (near upper = overbought, near lower = oversold)
  * Band squeeze or expansion indicating volatility changes
  * ATR level for position sizing and stop-loss recommendations
  * Breakout potential

## Volume Confirmation
- Present VWMA value
- Write 2-3 sentences analyzing:
  * Price vs VWMA positioning
  * Volume-weighted trend strength
  * Institutional participation signals

## Trading Recommendation
Write 3-4 sentences with actionable insights:
- Bullish/Bearish/Neutral overall assessment
- Specific entry/exit levels based on indicators
- Risk management using ATR
- Key levels to watch

## Summary Table
Create a markdown table with all 12 indicators and their signals (Bullish/Bearish/Neutral).

**CRITICAL REQUIREMENTS:**
- DO NOT just list indicator values without analysis
- Each section MUST have 2-4 sentences of detailed text analysis explaining what the indicators mean
- Provide specific trading insights, not generic descriptions
- Write in English only, no Chinese text"""
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
                    "For your reference, the current date is {current_date}. The company we want to look at is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

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
            "market_report": report,
        }

    return market_analyst_node
