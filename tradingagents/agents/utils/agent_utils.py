from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from typing import List
from typing import Annotated
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import RemoveMessage
from langchain_core.tools import tool
from datetime import date, timedelta, datetime
import functools
import pandas as pd
import yfinance as yf
import os
from dateutil.relativedelta import relativedelta
from langchain_openai import ChatOpenAI
import tradingagents.dataflows.interface as interface
from tradingagents.default_config import DEFAULT_CONFIG
from langchain_core.messages import HumanMessage


def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]
        
        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]
        
        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")
        
        return {"messages": removal_operations + [placeholder]}
    
    return delete_messages


class Toolkit:
    _config = DEFAULT_CONFIG.copy()

    @classmethod
    def update_config(cls, config):
        """Update the class-level configuration."""
        cls._config.update(config)

    @property
    def config(self):
        """Access the configuration."""
        return self._config

    def __init__(self, config=None):
        if config:
            self.update_config(config)

    @staticmethod
    @tool
    def get_reddit_news(
        curr_date: Annotated[str, "Date you want to get news for in yyyy-mm-dd format"],
    ) -> str:
        """
        Retrieve global news from Reddit within a specified time frame.
        Args:
            curr_date (str): Date you want to get news for in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing the latest global news from Reddit in the specified time frame.
        """
        
        global_news_result = interface.get_reddit_global_news(curr_date, 7, 5)

        return global_news_result

    @staticmethod
    @tool
    def get_finnhub_news(
        ticker: Annotated[
            str,
            "Search query of a company, e.g. 'AAPL, TSM, etc.",
        ],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news about a given stock from Finnhub within a date range
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            start_date (str): Start date in yyyy-mm-dd format
            end_date (str): End date in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing news about the company within the date range from start_date to end_date
        """

        end_date_str = end_date

        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        look_back_days = (end_date - start_date).days

        finnhub_news_result = interface.get_finnhub_news(
            ticker, end_date_str, look_back_days
        )

        return finnhub_news_result

    @staticmethod
    @tool
    def get_reddit_stock_info(
        ticker: Annotated[
            str,
            "Ticker of a company. e.g. AAPL, TSM",
        ],
        curr_date: Annotated[str, "Current date you want to get news for"],
    ) -> str:
        """
        Retrieve the latest news about a given stock from Reddit, given the current date.
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            curr_date (str): current date in yyyy-mm-dd format to get news for
        Returns:
            str: A formatted dataframe containing the latest news about the company on the given date
        """

        stock_news_results = interface.get_reddit_company_news(ticker, curr_date, 7, 5)

        return stock_news_results

    @staticmethod
    @tool
    def get_YFin_data(
        symbol: Annotated[str, "ticker symbol of the company"],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ) -> str:
        """
        Retrieve the stock price data for a given ticker symbol from Yahoo Finance.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            start_date (str): Start date in yyyy-mm-dd format
            end_date (str): End date in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing the stock price data for the specified ticker symbol in the specified date range.
        """

        result_data = interface.get_YFin_data(symbol, start_date, end_date)

        return result_data

    @staticmethod
    @tool
    def get_YFin_data_online(
        symbol: Annotated[str, "ticker symbol of the company"],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ) -> str:
        """
        Retrieve the stock price data for a given ticker symbol from Yahoo Finance.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            start_date (str): Start date in yyyy-mm-dd format
            end_date (str): End date in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing the stock price data for the specified ticker symbol in the specified date range.
        """

        result_data = interface.get_YFin_data_online(symbol, start_date, end_date)

        return result_data

    @staticmethod
    @tool
    def get_stockstats_indicators_report(
        symbol: Annotated[str, "ticker symbol of the company"],
        indicator: Annotated[
            str, "technical indicator to get the analysis and report of"
        ],
        curr_date: Annotated[
            str, "The current trading date you are trading on, YYYY-mm-dd"
        ],
        look_back_days: Annotated[int, "how many days to look back"] = 30,
    ) -> str:
        """
        Retrieve stock stats indicators for a given ticker symbol and indicator.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            indicator (str): Technical indicator to get the analysis and report of
            curr_date (str): The current trading date you are trading on, YYYY-mm-dd
            look_back_days (int): How many days to look back, default is 30
        Returns:
            str: A formatted dataframe containing the stock stats indicators for the specified ticker symbol and indicator.
        """

        result_stockstats = interface.get_stock_stats_indicators_window(
            symbol, indicator, curr_date, look_back_days, False
        )

        return result_stockstats

    @staticmethod
    @tool
    def get_stockstats_indicators_report_online(
        symbol: Annotated[str, "ticker symbol of the company"],
        indicator: Annotated[
            str, "technical indicator to get the analysis and report of"
        ],
        curr_date: Annotated[
            str, "The current trading date you are trading on, YYYY-mm-dd"
        ],
        look_back_days: Annotated[int, "how many days to look back"] = 30,
    ) -> str:
        """
        Retrieve stock stats indicators for a given ticker symbol and indicator.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            indicator (str): Technical indicator to get the analysis and report of
            curr_date (str): The current trading date you are trading on, YYYY-mm-dd
            look_back_days (int): How many days to look back, default is 30
        Returns:
            str: A formatted dataframe containing the stock stats indicators for the specified ticker symbol and indicator.
        """

        result_stockstats = interface.get_stock_stats_indicators_window(
            symbol, indicator, curr_date, look_back_days, True
        )

        return result_stockstats

    @staticmethod
    @tool
    def get_finnhub_company_insider_sentiment(
        ticker: Annotated[str, "ticker symbol for the company"],
        curr_date: Annotated[
            str,
            "current date of you are trading at, yyyy-mm-dd",
        ],
    ):
        """
        Retrieve insider sentiment information about a company (retrieved from public SEC information) for the past 30 days
        Args:
            ticker (str): ticker symbol of the company
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
            str: a report of the sentiment in the past 30 days starting at curr_date
        """

        data_sentiment = interface.get_finnhub_company_insider_sentiment(
            ticker, curr_date, 30
        )

        return data_sentiment

    @staticmethod
    @tool
    def get_finnhub_company_insider_transactions(
        ticker: Annotated[str, "ticker symbol"],
        curr_date: Annotated[
            str,
            "current date you are trading at, yyyy-mm-dd",
        ],
    ):
        """
        Retrieve insider transaction information about a company (retrieved from public SEC information) for the past 30 days
        Args:
            ticker (str): ticker symbol of the company
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
            str: a report of the company's insider transactions/trading information in the past 30 days
        """

        data_trans = interface.get_finnhub_company_insider_transactions(
            ticker, curr_date, 30
        )

        return data_trans

    @staticmethod
    @tool
    def get_simfin_balance_sheet(
        ticker: Annotated[str, "ticker symbol"],
        freq: Annotated[
            str,
            "reporting frequency: annual or quarterly",
        ] = "annual",
        curr_date: Annotated[str, "current date (optional), yyyy-mm-dd"] = None,
    ):
        """
        Retrieve the most recent balance sheet of a company using live data from Yahoo Finance.
        Args:
            ticker (str): ticker symbol of the company
            freq (str): reporting frequency: annual or quarterly (default: annual)
            curr_date (str): current date (optional), yyyy-mm-dd
        Returns:
            str: a report of the company's most recent balance sheet
        """
        
        try:
            # Use Yahoo Finance for live data instead of old SimFin CSV files
            stock = yf.Ticker(ticker)
            
            if freq.lower() == "quarterly":
                balance_sheet = stock.quarterly_balance_sheet
                freq_label = "Quarterly"
            else:
                balance_sheet = stock.balance_sheet
                freq_label = "Annual"
            
            if balance_sheet is None or balance_sheet.empty:
                # Fallback to SimFin if YFinance fails and curr_date is provided
                if curr_date:
                    data_balance_sheet = interface.get_simfin_balance_sheet(ticker, freq, curr_date)
                    return data_balance_sheet
                return f"No balance sheet data available for {ticker}"
            
            # Format the balance sheet nicely
            report = f"## {freq_label} Balance Sheet for {ticker} (Live Data from Yahoo Finance):\n\n"
            
            # Get the most recent period
            if len(balance_sheet.columns) > 0:
                latest_period = balance_sheet.columns[0]
                report += f"**Period:** {latest_period.strftime('%Y-%m-%d')}\n\n"
                
                # Format key metrics
                report += "### Key Metrics:\n"
                key_metrics = [
                    ('Total Assets', 'Total Assets'),
                    ('Current Assets', 'Current Assets'),
                    ('Cash And Cash Equivalents', 'Cash and Equivalents'),
                    ('Total Liabilities Net Minority Interest', 'Total Liabilities'),
                    ('Current Liabilities', 'Current Liabilities'),
                    ('Total Debt', 'Total Debt'),
                    ('Stockholders Equity', 'Stockholders Equity'),
                    ('Retained Earnings', 'Retained Earnings'),
                ]
                
                for metric_name, display_name in key_metrics:
                    if metric_name in balance_sheet.index:
                        value = balance_sheet.loc[metric_name, latest_period]
                        if not pd.isna(value):
                            report += f"- **{display_name}:** ${value:,.0f}\n"
                
                # Add full data table
                report += f"\n### Complete Balance Sheet:\n"
                report += balance_sheet.to_string()
                
            return report
            
        except Exception as e:
            print(f"Warning: Could not fetch live data from Yahoo Finance: {e}")
            # Fallback to SimFin if curr_date is provided
            if curr_date:
                data_balance_sheet = interface.get_simfin_balance_sheet(ticker, freq, curr_date)
                return data_balance_sheet
            return f"Unable to fetch balance sheet for {ticker}. Error: {str(e)}"

    @staticmethod
    @tool
    def get_simfin_cashflow(
        ticker: Annotated[str, "ticker symbol"],
        freq: Annotated[
            str,
            "reporting frequency: annual or quarterly",
        ] = "annual",
        curr_date: Annotated[str, "current date (optional), yyyy-mm-dd"] = None,
    ):
        """
        Retrieve the most recent cash flow statement of a company using live data from Yahoo Finance.
        Args:
            ticker (str): ticker symbol of the company
            freq (str): reporting frequency: annual or quarterly (default: annual)
            curr_date (str): current date (optional), yyyy-mm-dd
        Returns:
                str: a report of the company's most recent cash flow statement
        """
        
        try:
            # Use Yahoo Finance for live data instead of old SimFin CSV files
            stock = yf.Ticker(ticker)
            
            if freq.lower() == "quarterly":
                cashflow = stock.quarterly_cashflow
                freq_label = "Quarterly"
            else:
                cashflow = stock.cashflow
                freq_label = "Annual"
            
            if cashflow is None or cashflow.empty:
                # Fallback to SimFin if YFinance fails and curr_date is provided
                if curr_date:
                    data_cashflow = interface.get_simfin_cashflow(ticker, freq, curr_date)
                    return data_cashflow
                return f"No cash flow data available for {ticker}"
            
            # Format the cash flow statement nicely
            report = f"## {freq_label} Cash Flow Statement for {ticker} (Live Data from Yahoo Finance):\n\n"
            
            # Get the most recent period
            if len(cashflow.columns) > 0:
                latest_period = cashflow.columns[0]
                report += f"**Period:** {latest_period.strftime('%Y-%m-%d')}\n\n"
                
                # Format key metrics
                report += "### Key Metrics:\n"
                key_metrics = [
                    ('Operating Cash Flow', 'Operating Cash Flow'),
                    ('Free Cash Flow', 'Free Cash Flow'),
                    ('Investing Cash Flow', 'Investing Cash Flow'),
                    ('Financing Cash Flow', 'Financing Cash Flow'),
                    ('Capital Expenditure', 'Capital Expenditure'),
                    ('Issuance Of Debt', 'Debt Issuance'),
                    ('Repayment Of Debt', 'Debt Repayment'),
                    ('Common Stock Dividend Paid', 'Dividends Paid'),
                ]
                
                for metric_name, display_name in key_metrics:
                    if metric_name in cashflow.index:
                        value = cashflow.loc[metric_name, latest_period]
                        if not pd.isna(value):
                            report += f"- **{display_name}:** ${value:,.0f}\n"
                
                # Add full data table
                report += f"\n### Complete Cash Flow Statement:\n"
                report += cashflow.to_string()
                
            return report
            
        except Exception as e:
            print(f"Warning: Could not fetch live data from Yahoo Finance: {e}")
            # Fallback to SimFin if curr_date is provided
            if curr_date:
                data_cashflow = interface.get_simfin_cashflow(ticker, freq, curr_date)
                return data_cashflow
            return f"Unable to fetch cash flow for {ticker}. Error: {str(e)}"

    @staticmethod
    @tool
    def get_simfin_income_stmt(
        ticker: Annotated[str, "ticker symbol"],
        freq: Annotated[
            str,
            "reporting frequency: annual or quarterly",
        ] = "annual",
        curr_date: Annotated[str, "current date (optional), yyyy-mm-dd"] = None,
    ):
        """
        Retrieve the most recent income statement of a company using live data from Yahoo Finance.
        Args:
            ticker (str): ticker symbol of the company
            freq (str): reporting frequency: annual or quarterly (default: annual)
            curr_date (str): current date (optional), yyyy-mm-dd
        Returns:
                str: a report of the company's most recent income statement
        """
        
        try:
            # Use Yahoo Finance for live data instead of old SimFin CSV files
            stock = yf.Ticker(ticker)
            
            if freq.lower() == "quarterly":
                income_stmt = stock.quarterly_financials
                freq_label = "Quarterly"
            else:
                income_stmt = stock.financials
                freq_label = "Annual"
            
            if income_stmt is None or income_stmt.empty:
                # Fallback to SimFin if YFinance fails and curr_date is provided
                if curr_date:
                    data_income_stmt = interface.get_simfin_income_statements(
                        ticker, freq, curr_date
                    )
                    return data_income_stmt
                return f"No income statement data available for {ticker}"
            
            # Format the income statement nicely
            report = f"## {freq_label} Income Statement for {ticker} (Live Data from Yahoo Finance):\n\n"
            
            # Get the most recent period
            if len(income_stmt.columns) > 0:
                latest_period = income_stmt.columns[0]
                report += f"**Period:** {latest_period.strftime('%Y-%m-%d')}\n\n"
                
                # Format key metrics
                report += "### Key Metrics:\n"
                key_metrics = [
                    ('Total Revenue', 'Revenue'),
                    ('Cost Of Revenue', 'Cost of Revenue'),
                    ('Gross Profit', 'Gross Profit'),
                    ('Operating Expense', 'Operating Expenses'),
                    ('Operating Income', 'Operating Income'),
                    ('EBITDA', 'EBITDA'),
                    ('Net Income', 'Net Income'),
                    ('Basic EPS', 'Earnings Per Share'),
                ]
                
                for metric_name, display_name in key_metrics:
                    if metric_name in income_stmt.index:
                        value = income_stmt.loc[metric_name, latest_period]
                        if not pd.isna(value):
                            report += f"- **{display_name}:** ${value:,.0f}\n"
                
                # Add full data table
                report += f"\n### Complete Income Statement:\n"
                report += income_stmt.to_string()
                
            return report
            
        except Exception as e:
            print(f"Warning: Could not fetch live data from Yahoo Finance: {e}")
            # Fallback to SimFin if curr_date is provided
            if curr_date:
                data_income_stmt = interface.get_simfin_income_statements(
                    ticker, freq, curr_date
                )
                return data_income_stmt
            return f"Unable to fetch income statement for {ticker}. Error: {str(e)}"

    @staticmethod
    @tool
    def get_google_news(
        query: Annotated[str, "Query to search with"],
        curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news from Google News based on a query and date range.
        Args:
            query (str): Query to search with
            curr_date (str): Current date in yyyy-mm-dd format
            look_back_days (int): How many days to look back
        Returns:
            str: A formatted string containing the latest news from Google News based on the query and date range.
        """

        google_news_results = interface.get_google_news(query, curr_date, 7)

        return google_news_results

# REMOVED: get_stock_news_openai - Not providing real-time news, just LLM hallucinations

# REMOVED: get_global_news_openai - Not providing real-time news, just LLM hallucinations

    @staticmethod
    @tool
    def get_fundamentals_openai(
        ticker: Annotated[str, "the company's ticker"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest fundamental information about a given stock on a given date by using OpenAI's news API.
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            curr_date (str): Current date in yyyy-mm-dd format
        Returns:
            str: A formatted string containing the latest fundamental information about the company on the given date.
        """

        openai_fundamentals_results = interface.get_fundamentals_openai(
            ticker, curr_date
        )

        return openai_fundamentals_results
