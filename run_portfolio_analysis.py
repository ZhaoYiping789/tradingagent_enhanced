#!/usr/bin/env python3
"""
Multi-Stock Portfolio Analysis System
Analyzes multiple stocks and generates optimized portfolio recommendations
"""

import sys
import os
from datetime import date
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
    """Main portfolio analysis function"""
    
    print("=" * 80)
    print("TRADINGAGENTS MULTI-STOCK PORTFOLIO ANALYSIS")
    print("=" * 80)
    
    # Configuration
    # Use 2025-10-03 where we have NVDA analysis
    current_date = "2025-10-03"  # date.today().strftime("%Y-%m-%d")
    
    # Stocks to analyze (start with ones we have data for)
    tickers = ["NVDA"]  # Add more after running analyses for them
    print(f"\nTarget Portfolio: {', '.join(tickers)}")
    print(f"Analysis Date: {current_date}")
    
    # OPTION 1: Use existing single-stock analyses (if available)
    print("\n" + "=" * 80)
    print("STEP 1: Loading Existing Stock Analyses")
    print("=" * 80)
    
    aggregator = StockDataAggregator(current_date)
    aggregated_result = aggregator.aggregate_multiple_stocks(tickers)
    
    if aggregated_result['num_stocks'] == 0:
        print("\nWARNING: No existing analyses found!")
        print("Please run single-stock analysis for each ticker first using:")
        print("  uv run main_enterprise.py")
        print("\nOr uncomment STEP 2 below to run analyses automatically.")
        return
    
    print(f"\nLoaded {aggregated_result['num_stocks']} stock analyses")
    print("\nComparison Summary:")
    print(aggregated_result['comparison_df'].to_string())
    
    # OPTION 2: Run analyses if needed (commented out for now)
    # Uncomment this section to automatically analyze stocks
    """
    print("\n" + "=" * 80)
    print("STEP 2: Running Single-Stock Analyses (if needed)")
    print("=" * 80)
    
    # Setup configuration
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "openai"
    config["backend_url"] = "https://api.laozhang.ai/v1"
    config["deep_think_llm"] = "gpt-4o"
    config["quick_think_llm"] = "gpt-4o-mini"
    config["online_tools"] = True
    
    selected_analysts = ["market", "fundamentals", "comprehensive_quantitative"]
    
    ta = TradingAgentsGraph(
        selected_analysts=selected_analysts,
        debug=False,
        config=config
    )
    
    for ticker in tickers:
        if ticker not in aggregated_result['stocks_data']:
            print(f"\nAnalyzing {ticker}...")
            try:
                final_state, decision = ta.propagate(ticker, current_date)
                print(f"  SUCCESS: {ticker} - {decision}")
            except Exception as e:
                print(f"  ERROR: {ticker} - {e}")
    
    # Reload aggregated data
    aggregated_result = aggregator.aggregate_multiple_stocks(tickers)
    """
    
    # STEP 3: Get returns data for optimization
    print("\n" + "=" * 80)
    print("STEP 2: Fetching Price Data for Optimization")
    print("=" * 80)
    
    returns_data = {}
    for ticker in aggregated_result['stocks_data'].keys():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")
            if not hist.empty:
                returns_data[ticker] = hist['Close'].pct_change().dropna()
                print(f"  {ticker}: {len(returns_data[ticker])} days of data")
        except Exception as e:
            print(f"  ERROR {ticker}: {e}")
    
    if len(returns_data) < 2:
        print("\nERROR: Need at least 2 stocks for portfolio optimization")
        return
    
    # Create returns DataFrame
    returns_df = pd.DataFrame(returns_data).dropna()
    print(f"\nReturns matrix: {returns_df.shape[0]} days x {returns_df.shape[1]} stocks")
    
    # STEP 4: Run Portfolio Optimization
    print("\n" + "=" * 80)
    print("STEP 3: Running Multi-Scenario Portfolio Optimization")
    print("=" * 80)
    
    stock_metrics = {ticker: data['metrics'] for ticker, data in aggregated_result['stocks_data'].items() if ticker in returns_df.columns}
    
    optimizer = MultiScenarioPortfolioOptimizer(returns_df, stock_metrics)
    optimization_scenarios = optimizer.optimize_all_scenarios()
    
    print("\nOptimization Scenarios Generated:")
    for scenario_name, scenario_data in optimization_scenarios.items():
        print(f"  {scenario_data['method']}: Sharpe={scenario_data['sharpe_ratio']:.2f}")
    
    # STEP 5: Generate Portfolio Report
    print("\n" + "=" * 80)
    print("STEP 4: Generating Portfolio Report")
    print("=" * 80)
    
    report_generator = PortfolioReportGenerator(
        aggregated_result,
        optimization_scenarios,
        current_date
    )
    
    report_path = report_generator.generate_comprehensive_report()
    
    # STEP 6: Display Summary
    print("\n" + "=" * 80)
    print("PORTFOLIO ANALYSIS COMPLETE")
    print("=" * 80)
    
    print(f"\nAnalyzed Stocks: {', '.join(aggregated_result['stocks_data'].keys())}")
    print(f"Optimization Scenarios: {len(optimization_scenarios)}")
    print(f"\nReport Location: {report_path}")
    
    print("\nTop 3 Scenarios by Sharpe Ratio:")
    scenarios_sorted = sorted(optimization_scenarios.items(), key=lambda x: x[1]['sharpe_ratio'], reverse=True)
    for i, (name, data) in enumerate(scenarios_sorted[:3], 1):
        top_stock = max(data['weights'].items(), key=lambda x: x[1])
        print(f"  {i}. {data['method']}: Sharpe={data['sharpe_ratio']:.2f}, Top holding: {top_stock[0]} ({top_stock[1]*100:.0f}%)")
    
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("  1. Review portfolio report: " + report_path)
    print("  2. Portfolio Trader will integrate these scenarios with LLM judgment")
    print("  3. Final portfolio allocation will be generated")
    print("=" * 80)
    
    return report_path


if __name__ == "__main__":
    main()
