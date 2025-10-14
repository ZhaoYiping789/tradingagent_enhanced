#!/usr/bin/env python3
"""
TradingAgents Enterprise Edition - WatsonX Version
Enhanced trading analysis system with IBM WatsonX.ai integration
Supports both single-stock and multi-stock portfolio analysis
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.analysts.enterprise_strategy_analyst import create_enterprise_strategy_analyst
from tradingagents.agents.generators.enhanced_quantitative_document_generator import create_enhanced_quantitative_document_generator
from tradingagents.agents.trader.enterprise_trader import create_enterprise_trader
from tradingagents.portfolio.stock_data_aggregator import StockDataAggregator
from tradingagents.portfolio.multi_scenario_portfolio_optimizer import MultiScenarioPortfolioOptimizer
from tradingagents.portfolio.portfolio_report_generator import PortfolioReportGenerator
from datetime import date
import os
import sys
import time
import pandas as pd
import yfinance as yf

def main():
    """Enterprise-level main function with WatsonX LLM integration."""

    # Set console encoding for Windows
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

    # Create log file for frontend monitoring
    log_file = "enterprise_watsonx_output.log"

    def log_print(text):
        """Print to both console and log file"""
        print(text)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(text + '\n')

    # Clear previous logs
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("")

    log_print("🏛️ TRADINGAGENTS ENTERPRISE EDITION - WATSONX")
    log_print("=" * 80)
    log_print("🎯 Institutional-Grade Analysis with IBM WatsonX.ai")
    log_print("=" * 80)

    # Set WatsonX API credentials
    # IMPORTANT: Set these environment variables before running
    # Or use hardcoded values below for testing
    watsonx_api_key = os.getenv("WATSONX_APIKEY") or os.getenv("WATSONX_API_KEY") or "1NlP-L5h1DDEZFKkvJ92uTuMFNbkk0pmGJ4lMutJ44w2"
    watsonx_project_id = os.getenv("WATSONX_PROJECT_ID") or "394811a9-3e1c-4b80-8031-3fda71e6dce1"
    watsonx_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

    # Set dummy OpenAI key for memory system (uses OpenAI embeddings)
    # TODO: Update memory system to support WatsonX embeddings
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "dummy-key-for-testing"

    if not watsonx_api_key or not watsonx_project_id:
        log_print("❌ ERROR: WatsonX credentials not set!")
        log_print("Please set the following environment variables:")
        log_print("  Windows: set_watsonx_env.bat")
        log_print("  Linux/Mac: source set_watsonx_env.sh")
        log_print("")
        log_print("Or set manually:")
        log_print("  set WATSONX_APIKEY=your-api-key")
        log_print("  set WATSONX_PROJECT_ID=your-project-id")
        log_print("  set WATSONX_URL=https://us-south.ml.cloud.ibm.com")
        return

    log_print(f"✅ WatsonX URL: {watsonx_url}")
    log_print(f"✅ WatsonX Project ID: {watsonx_project_id[:20]}...")
    log_print("")

    # Create enhanced enterprise config for WatsonX
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "watsonx"
    config["watsonx_url"] = watsonx_url
    config["watsonx_project_id"] = watsonx_project_id
    config["watsonx_api_key"] = watsonx_api_key

    # WatsonX Model Configuration
    # Available models in your environment:
    # - "meta-llama/llama-3-3-70b-instruct" (Llama 3.3 70B - Best quality)
    # - "ibm/granite-3-3-8b-instruct" (Granite 3.3 8B - Balanced)
    # - "ibm/granite-3-8b-instruct" (Granite 3.0 8B - Lightweight)
    # - "mistralai/mistral-medium-2505" (Mistral Medium - Good alternative)
    config["deep_think_llm"] = "meta-llama/llama-3-3-70b-instruct"  # Complex analysis
    config["quick_think_llm"] = "ibm/granite-3-3-8b-instruct"  # Quick operations (faster)

    # Generation parameters
    config["max_tokens"] = 32768  # Maximum tokens for huge prompts and outputs (Llama 3.3 70B supports up to 128K context)
    config["temperature"] = 0.7

    # Enterprise settings
    config["max_debate_rounds"] = 2  # More thorough debate
    config["max_risk_discuss_rounds"] = 2  # Enhanced risk analysis
    config["online_tools"] = True
    config["lightweight_quantitative"] = False  # Enable full optimization algorithms
    config["enterprise_mode"] = True  # Enable enterprise features
    config["use_comprehensive_quantitative"] = True  # Enable comprehensive quantitative analysis
    config["include_optimization_results"] = True  # Include mathematical optimization

    # Enhanced analyst selection for enterprise analysis with full sentiment
    selected_analysts = [
        "market",          # Advanced technical analysis
        "social",          # Sentiment analysis with social signals
        "news",            # Comprehensive news analysis
        "fundamentals",    # Deep fundamental analysis
        "comprehensive_quantitative",  # ENHANCED: Comprehensive quantitative with optimization
        "portfolio",       # Portfolio impact analysis
        "enterprise_strategy"  # NEW: Enterprise strategy analyst
    ]

    log_print(f"📊 Enterprise Analysts Selected: {', '.join(selected_analysts)}")
    log_print(f"🤖 LLM Provider: IBM WatsonX.ai")
    log_print(f"🧠 Deep Thinking Model: {config['deep_think_llm']}")
    log_print(f"⚡ Quick Thinking Model: {config['quick_think_llm']}")
    log_print("")

    # Initialize the enterprise trading agents graph
    log_print("🔧 Initializing Enterprise TradingAgents System with WatsonX...")
    try:
        ta = TradingAgentsGraph(
            selected_analysts=selected_analysts,
            debug=True,
            config=config
        )
    except ImportError as e:
        log_print(f"❌ ERROR: {e}")
        log_print("")
        log_print("Please install WatsonX dependencies:")
        log_print("  uv pip install langchain-ibm ibm-watsonx-ai")
        return
    except Exception as e:
        log_print(f"❌ ERROR initializing TradingAgents: {e}")
        import traceback
        traceback.print_exc()
        return

    # Enterprise components are integrated through selected_analysts
    log_print("⚡ Enterprise Components Integrated Successfully...")

    # Get current date and tickers for analysis
    current_date = "2025-10-10"

    # PORTFOLIO MODE: Analyze multiple stocks
    portfolio_mode = False  # Set to True for portfolio analysis
    portfolio_tickers = ["NVDA", "AAPL", "MSFT", "GOOGL", "TSLA"]

    log_print(f"📅 ANALYSIS DATE: {current_date}")

    if portfolio_mode:
        log_print(f"📊 PORTFOLIO MODE: Analyzing {len(portfolio_tickers)} stocks")
        log_print(f"🎯 TARGET SECURITIES: {', '.join(portfolio_tickers)}")
    else:
        ticker = "NVDA"
        log_print(f"🎯 TARGET SECURITY: {ticker}")

    log_print("=" * 80)

    # Start comprehensive enterprise analysis
    log_print("🚀 INITIATING ENTERPRISE-LEVEL ANALYSIS WITH WATSONX...")
    log_print("")
    log_print("📋 ANALYSIS COMPONENTS:")
    log_print("   🔍 Advanced Technical Analysis")
    log_print("   📊 Multi-Source Sentiment Analysis")
    log_print("   📰 Comprehensive News Intelligence")
    log_print("   💰 Deep Fundamental Analysis")
    log_print("   🤖 Machine Learning Forecasting")
    log_print("   🏛️ Investment Committee Debate")
    log_print("   ⚖️ Advanced Risk Assessment")
    log_print("   🎯 Enterprise Strategy Generation")
    log_print("   💼 Institutional Trading Plan")
    log_print("   📊 Professional Report Generation")
    log_print("")

    try:
        start_time = time.time()

        if portfolio_mode:
            # PORTFOLIO MODE: Analyze each stock then generate portfolio
            log_print("⏳ Running Multi-Stock Analysis Pipeline...")
            log_print("")

            stock_results = {}
            for i, ticker in enumerate(portfolio_tickers, 1):
                log_print(f"📊 [{i}/{len(portfolio_tickers)}] Analyzing {ticker}...")
                log_print("-" * 80)

                try:
                    final_state, decision = ta.propagate(ticker, current_date)
                    stock_results[ticker] = {
                        'state': final_state,
                        'decision': decision
                    }
                    log_print(f"✅ {ticker} Analysis Complete - Decision: {decision}")
                    log_print("")
                except Exception as e:
                    log_print(f"❌ {ticker} Analysis Failed: {e}")
                    log_print("")

            analysis_time = time.time() - start_time

            # Generate Portfolio Report
            if len(stock_results) >= 2:
                log_print("")
                log_print("=" * 80)
                log_print("📊 GENERATING PORTFOLIO ANALYSIS")
                log_print("=" * 80)

                try:
                    # Aggregate stock data
                    aggregator = StockDataAggregator(current_date)
                    aggregated_result = aggregator.aggregate_multiple_stocks(list(stock_results.keys()))

                    if aggregated_result['num_stocks'] >= 2:
                        log_print(f"✅ Loaded {aggregated_result['num_stocks']} stock analyses")

                        # Get returns data
                        log_print("📈 Fetching price data for optimization...")
                        returns_data = {}
                        for ticker in stock_results.keys():
                            stock_data = yf.download(ticker, period='6mo', progress=False)
                            if not stock_data.empty:
                                # Handle MultiIndex columns from yfinance
                                if isinstance(stock_data.columns, pd.MultiIndex):
                                    close_prices = stock_data[('Close', ticker)]
                                else:
                                    close_prices = stock_data['Close']

                                returns = close_prices.pct_change().dropna()
                                returns_data[ticker] = returns

                        returns_df = pd.DataFrame(returns_data).dropna()
                        log_print(f"✅ Returns matrix: {returns_df.shape}")

                        # Run portfolio optimization
                        log_print("🎯 Running multi-scenario portfolio optimization...")
                        stock_metrics = {ticker: data['metrics'] for ticker, data in aggregated_result['stocks_data'].items()}
                        optimizer = MultiScenarioPortfolioOptimizer(returns_df, stock_metrics)
                        optimization_scenarios = optimizer.optimize_all_scenarios()
                        log_print(f"✅ Generated {len(optimization_scenarios)} portfolio scenarios")

                        # Generate portfolio report
                        log_print("📄 Generating portfolio report...")
                        report_gen = PortfolioReportGenerator(aggregated_result, optimization_scenarios, current_date)
                        portfolio_report_path = report_gen.generate_comprehensive_report()
                        log_print(f"✅ Portfolio report: {portfolio_report_path}")
                    else:
                        log_print("⚠️  Insufficient data for portfolio optimization")

                except Exception as e:
                    log_print(f"❌ Portfolio generation failed: {e}")
                    import traceback
                    traceback.print_exc()
        else:
            # SINGLE STOCK MODE
            log_print("⏳ Running Multi-Agent Analysis Pipeline...")
            final_state, decision = ta.propagate(ticker, current_date)
            analysis_time = time.time() - start_time

        log_print("")
        log_print("=" * 80)
        log_print("✅ ENTERPRISE ANALYSIS COMPLETE!")
        log_print(f"⏱️  Total Analysis Time: {analysis_time:.1f} seconds")
        log_print("=" * 80)

        # Display comprehensive results
        log_print("")
        log_print("📊 EXECUTIVE SUMMARY:")
        log_print(f"   🎯 Final Decision: {decision}")
        log_print(f"   💪 Confidence Level: {final_state.get('decision_confidence', 'Medium')}")

        if final_state.get("enterprise_strategy"):
            log_print(f"   📈 Strategy Generated: Advanced Trading Plan")

        if final_state.get("enterprise_document"):
            log_print(f"   📄 Enterprise Report: Institutional-Grade Document")

        # Show file locations
        log_print("")
        log_print("📁 OUTPUT LOCATIONS:")

        results_dir = f"results/{ticker}/{current_date}"
        log_print(f"   📊 Standard Reports: {results_dir}/")

        if final_state.get("enterprise_document_path"):
            log_print(f"   🏛️ Enterprise Report: {final_state['enterprise_document_path']}")

        eval_dir = f"eval_results/{ticker}/TradingAgentsStrategy_logs"
        log_print(f"   📋 Detailed Logs: {eval_dir}/")

        log_print("")
        log_print("=" * 80)
        log_print("🎉 WATSONX ENTERPRISE TRADINGAGENTS ANALYSIS COMPLETE!")
        log_print(f"🎯 INSTITUTIONAL RECOMMENDATION: {decision}")
        log_print("🏛️ Ready for Investment Committee Review")
        log_print("=" * 80)

    except Exception as e:
        log_print("")
        log_print("❌ ERROR DURING ENTERPRISE ANALYSIS")
        log_print(f"Error Details: {str(e)}")
        log_print("Please check your configuration and try again.")
        log_print("")
        import traceback
        traceback.print_exc()
        return

    log_print("")
    log_print("📊 Enterprise analysis complete. Review generated reports for detailed insights.")

if __name__ == "__main__":
    main()
