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
            """You are a trading assistant tasked with performing COMPREHENSIVE technical analysis. You MUST analyze ALL of the following REQUIRED indicators to provide a complete picture:

**REQUIRED INDICATORS (You MUST call ALL of these):**

Moving Averages (REQUIRED):
- close_50_sma: 50 SMA - Medium-term trend indicator for identifying trend direction and support/resistance
- close_200_sma: 200 SMA - Long-term trend benchmark for confirming overall market trend and golden/death cross setups
- close_10_ema: 10 EMA - Short-term momentum indicator for capturing quick shifts and entry points

MACD Related (REQUIRED - ALL THREE):
- macd: MACD Line - Momentum via EMA differences. CRITICAL for identifying trend changes and divergence
- macds: MACD Signal Line - Smoothing of MACD. CRITICAL for crossover signals
- macdh: MACD Histogram - Gap between MACD and signal. CRITICAL for visualizing momentum strength

Momentum Indicators (REQUIRED):
- rsi: RSI - Measures overbought/oversold conditions (70/30 thresholds) and divergence for reversals

Volatility Indicators (REQUIRED):
- boll: Bollinger Middle Band - 20 SMA baseline for price movement
- boll_ub: Bollinger Upper Band - 2 std dev above, signals overbought conditions and breakout zones
- boll_lb: Bollinger Lower Band - 2 std dev below, indicates oversold conditions
- atr: ATR - Measures volatility for setting stop-loss levels and position sizing

Volume-Based Indicators (REQUIRED):
- vwma: VWMA - Volume-weighted moving average to confirm trends with volume data

**CRITICAL INSTRUCTIONS:**
1. First call get_YFin_data to retrieve the CSV data
2. Then call get_stockstats_indicators_report for EACH of the 12 indicators listed above
3. Do NOT skip any indicators - they are ALL required for comprehensive analysis
4. After gathering all indicators, write a detailed report analyzing:
   - Trend analysis (using SMAs and EMAs)
   - Momentum analysis (using MACD, RSI)
   - Volatility analysis (using Bollinger Bands, ATR)
   - Volume confirmation (using VWMA)
5. Provide specific trading signals based on indicator crossovers, divergences, and levels
6. Include a comprehensive Markdown table summarizing all key indicators and their signals

When you tool call, use the EXACT indicator names as listed above. Write a very detailed and nuanced report with specific insights that help traders make informed decisions."""
            + """ **LANGUAGE REQUIREMENT**: Write EVERYTHING in English only. No Chinese text. Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""
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

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
