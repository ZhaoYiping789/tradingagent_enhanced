#!/usr/bin/env python3
"""
Multi-Stock Portfolio Analysis with WatsonX
Analyzes multiple stocks and generates optimized portfolio recommendations
"""

import sys
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
import yfinance as yf

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.portfolio.stock_data_aggregator import StockDataAggregator
from tradingagents.portfolio.multi_scenario_portfolio_optimizer import MultiScenarioPortfolioOptimizer
from tradingagents.portfolio.portfolio_report_generator import PortfolioReportGenerator


def main():
    """Main portfolio analysis function with WatsonX"""

    print("=" * 80)
    print("TRADINGAGENTS MULTI-STOCK PORTFOLIO ANALYSIS - WATSONX")
    print("=" * 80)

    # Configuration
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Stocks to analyze - Default: NVDA and AAPL
    tickers = ["NVDA", "AAPL"]
    print(f"\n📊 Target Portfolio: {', '.join(tickers)}")
    print(f"📅 Analysis Date: {current_date}")

    # STEP 1: Run individual stock analyses with WatsonX
    print("\n" + "=" * 80)
    print("STEP 1: Running Individual Stock Analyses with WatsonX")
    print("=" * 80)

    # WatsonX credentials
    watsonx_api_key = os.getenv("WATSONX_APIKEY") or os.getenv("WATSONX_API_KEY") or "1NlP-L5h1DDEZFKkvJ92uTuMFNbkk0pmGJ4lMutJ44w2"
    watsonx_project_id = os.getenv("WATSONX_PROJECT_ID") or "394811a9-3e1c-4b80-8031-3fda71e6dce1"
    watsonx_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "dummy-key-for-testing"

    # Setup WatsonX configuration
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "watsonx"
    config["watsonx_url"] = watsonx_url
    config["watsonx_project_id"] = watsonx_project_id
    config["watsonx_api_key"] = watsonx_api_key
    config["deep_think_llm"] = "meta-llama/llama-3-3-70b-instruct"
    config["quick_think_llm"] = "ibm/granite-3-3-8b-instruct"
    config["max_tokens"] = 32768
    config["temperature"] = 0.7
    config["max_debate_rounds"] = 2
    config["max_risk_discuss_rounds"] = 2
    config["online_tools"] = True
    config["lightweight_quantitative"] = False
    config["enterprise_mode"] = True
    config["use_comprehensive_quantitative"] = True
    config["include_optimization_results"] = True

    selected_analysts = [
        "market",
        "social",
        "news",
        "fundamentals",
        "comprehensive_quantitative",
        "portfolio",
        "enterprise_strategy"
    ]

    ta = TradingAgentsGraph(
        selected_analysts=selected_analysts,
        debug=True,
        config=config
    )

    # Analyze each stock
    for ticker in tickers:
        print(f"\n{'='*80}")
        print(f"🔍 Analyzing {ticker}...")
        print(f"{'='*80}")
        try:
            final_state, decision = ta.propagate(ticker, current_date)
            print(f"\n✅ SUCCESS: {ticker} - {decision}")
        except Exception as e:
            print(f"\n❌ ERROR: {ticker} - {e}")
            import traceback
            traceback.print_exc()

    # STEP 2: Aggregate stock data
    print("\n" + "=" * 80)
    print("STEP 2: Aggregating Stock Analyses")
    print("=" * 80)

    aggregator = StockDataAggregator(current_date)
    aggregated_result = aggregator.aggregate_multiple_stocks(tickers)

    if aggregated_result['num_stocks'] < 2:
        print(f"\n❌ WARNING: Only {aggregated_result['num_stocks']} stock(s) analyzed!")
        print("Need at least 2 stocks for portfolio optimization")
        return

    print(f"\n✅ Loaded {aggregated_result['num_stocks']} stock analyses")
    print("\n📊 Comparison Summary:")
    print(aggregated_result['comparison_df'].to_string())

    # STEP 3: Get returns data for optimization
    print("\n" + "=" * 80)
    print("STEP 3: Fetching Price Data for Optimization")
    print("=" * 80)

    returns_data = {}
    for ticker in aggregated_result['stocks_data'].keys():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")
            if not hist.empty:
                returns_data[ticker] = hist['Close'].pct_change().dropna()
                print(f"  ✅ {ticker}: {len(returns_data[ticker])} days of data")
        except Exception as e:
            print(f"  ❌ ERROR {ticker}: {e}")

    if len(returns_data) < 2:
        print("\n❌ ERROR: Need at least 2 stocks for portfolio optimization")
        return

    # Create returns DataFrame
    returns_df = pd.DataFrame(returns_data).dropna()
    print(f"\n📈 Returns matrix: {returns_df.shape[0]} days x {returns_df.shape[1]} stocks")

    # STEP 4: Run Portfolio Optimization
    print("\n" + "=" * 80)
    print("STEP 4: Running Multi-Scenario Portfolio Optimization")
    print("=" * 80)

    stock_metrics = {ticker: data['metrics'] for ticker, data in aggregated_result['stocks_data'].items() if ticker in returns_df.columns}

    optimizer = MultiScenarioPortfolioOptimizer(returns_df, stock_metrics)
    optimization_scenarios = optimizer.optimize_all_scenarios()

    print("\n🎯 Optimization Scenarios Generated:")
    for scenario_name, scenario_data in optimization_scenarios.items():
        print(f"  📊 {scenario_data['method']}: Sharpe={scenario_data['sharpe_ratio']:.2f}")
        for ticker, weight in scenario_data['weights'].items():
            print(f"     - {ticker}: {weight*100:.2f}%")

    # STEP 5: Generate Portfolio Report
    print("\n" + "=" * 80)
    print("STEP 5: Generating Portfolio Report with LLM Final Allocation")
    print("=" * 80)

    report_generator = PortfolioReportGenerator(
        aggregated_result,
        optimization_scenarios,
        current_date
    )

    report_path = report_generator.generate_comprehensive_report()

    # STEP 6: Display Summary
    print("\n" + "=" * 80)
    print("✅ PORTFOLIO ANALYSIS COMPLETE")
    print("=" * 80)

    print(f"\n📊 Analyzed Stocks: {', '.join(aggregated_result['stocks_data'].keys())}")
    print(f"🎯 Optimization Scenarios: {len(optimization_scenarios)}")
    print(f"\n📄 Report Location: {report_path}")

    print("\n🏆 Top 3 Scenarios by Sharpe Ratio:")
    scenarios_sorted = sorted(optimization_scenarios.items(), key=lambda x: x[1]['sharpe_ratio'], reverse=True)
    for i, (name, data) in enumerate(scenarios_sorted[:3], 1):
        top_stock = max(data['weights'].items(), key=lambda x: x[1])
        print(f"  {i}. {data['method']}: Sharpe={data['sharpe_ratio']:.2f}, Top holding: {top_stock[0]} ({top_stock[1]*100:.0f}%)")

    print("\n" + "=" * 80)
    print("✅ Next Steps:")
    print(f"  1. Review portfolio report: {report_path}")
    print("  2. Check LLM Portfolio Manager's final allocation decision")
    print("  3. Review 6-scenario optimization comparison table")
    print("=" * 80)

    return report_path


if __name__ == "__main__":
    # Set console encoding for Windows
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

    main()
