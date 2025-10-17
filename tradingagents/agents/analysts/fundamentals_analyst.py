from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_fundamentals_analyst(llm, toolkit):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        # Always use Yahoo Finance tools for live fundamental data
        tools = [
            toolkit.get_simfin_balance_sheet,  # Now uses Yahoo Finance with fallback
            toolkit.get_simfin_cashflow,       # Now uses Yahoo Finance with fallback
            toolkit.get_simfin_income_stmt,    # Now uses Yahoo Finance with fallback
        ]

        system_message = (
            f"You are a fundamental analyst for {ticker}. Your job is to analyze the company's financial statements and write a comprehensive report IN ENGLISH ONLY.\n\n"
            + "**WORKFLOW:**\n"
            + "Step 1: Call these three tools to get annual financial data (use freq='annual'):\n"
            + "- get_simfin_income_stmt\n"
            + "- get_simfin_balance_sheet\n"
            + "- get_simfin_cashflow\n\n"
            + "Step 2: AFTER you receive the tool results with actual data, write your analysis report with:\n\n"
            + "## Company Profile\n"
            + "Brief description of {ticker}\n\n"
            + "## Financial Performance (3-5 Year History)\n\n"
            + "### Income Statement Analysis\n"
            + "Create a markdown table with YEARS AS COLUMNS and METRICS AS ROWS:\n"
            + "| Metric | 2024 | 2023 | 2022 | 2021 | Avg Annual Change |\n"
            + "|--------|------|------|------|------|-------------------|\n"
            + "| Revenue ($B) | XX.X | XX.X | XX.X | XX.X | +XX.X% |\n"
            + "| Net Income ($B) | XX.X | XX.X | XX.X | XX.X | +XX.X% |\n"
            + "| EPS ($) | X.XX | X.XX | X.XX | X.XX | +XX.X% |\n"
            + "| Gross Margin (%) | XX.X | XX.X | XX.X | XX.X | +X.Xpp |\n"
            + "| Operating Margin (%) | XX.X | XX.X | XX.X | XX.X | +X.Xpp |\n\n"
            + "Calculate Avg Annual Change = (Latest / Oldest) ^ (1/years) - 1\n"
            + "Then write 2-3 sentences analyzing revenue growth trends, profitability changes, and margins.\n\n"
            + "### Balance Sheet Analysis\n"
            + "Create a markdown table with YEARS AS COLUMNS:\n"
            + "| Metric | 2024 | 2023 | 2022 | 2021 | Avg Annual Change |\n"
            + "|--------|------|------|------|------|-------------------|\n"
            + "| Total Assets ($B) | XXX | XXX | XXX | XXX | +XX.X% |\n"
            + "| Total Liabilities ($B) | XXX | XXX | XXX | XXX | +XX.X% |\n"
            + "| Stockholders Equity ($B) | XXX | XXX | XXX | XXX | +XX.X% |\n"
            + "| Total Debt ($B) | XX.X | XX.X | XX.X | XX.X | +XX.X% |\n"
            + "| Debt-to-Equity Ratio | X.XX | X.XX | X.XX | X.XX | N/A |\n\n"
            + "Then write 2-3 sentences analyzing balance sheet strength, leverage trends, and financial position.\n\n"
            + "### Cash Flow Analysis\n"
            + "Create a markdown table with YEARS AS COLUMNS:\n"
            + "| Metric | 2024 | 2023 | 2022 | 2021 | Avg Annual Change |\n"
            + "|--------|------|------|------|------|-------------------|\n"
            + "| Operating Cash Flow ($B) | XX.X | XX.X | XX.X | XX.X | +XX.X% |\n"
            + "| Free Cash Flow ($B) | XX.X | XX.X | XX.X | XX.X | +XX.X% |\n"
            + "| FCF Margin (%) | XX.X | XX.X | XX.X | XX.X | +X.Xpp |\n\n"
            + "Then write 2-3 sentences analyzing cash generation ability and trends.\n\n"
            + "## Overall Assessment\n"
            + "Write 2-3 paragraphs synthesizing all financial data: Is the company growing? Is it profitable? Is the financial position strong?\n\n"
            + "**CRITICAL**: \n"
            + "1. DO NOT just describe what tools to call. After you get the actual financial data from the tools, you MUST write the full analysis report with tables AND text analysis for each section.\n"
            + "2. Table format: Years MUST be in columns (horizontal), metrics in rows (vertical)\n"
            + "3. Calculate average annual growth rate using CAGR formula: ((Latest/Oldest)^(1/n_years) - 1) * 100%",
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
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
