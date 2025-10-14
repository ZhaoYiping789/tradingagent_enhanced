#!/usr/bin/env python3
"""
Test Report Regeneration with LLM Portfolio Manager
"""

import os
import sys

# Set console encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Set environment variables for WatsonX
os.environ["WATSONX_APIKEY"] = "1NlP-L5h1DDEZFKkvJ92uTuMFNbkk0pmGJ4lMutJ44w2"
os.environ["WATSONX_PROJECT_ID"] = "394811a9-3e1c-4b80-8031-3fda71e6dce1"
os.environ["WATSONX_URL"] = "https://us-south.ml.cloud.ibm.com"

from tradingagents.portfolio.stock_data_aggregator import StockDataAggregator
from tradingagents.portfolio.portfolio_report_generator import PortfolioReportGenerator

print("="*80)
print("Testing Report Regeneration with LLM Portfolio Manager")
print("="*80)

current_date = "2025-10-15"
tickers = ["NVDA", "AAPL"]

print(f"\n📊 Loading existing analysis data for {', '.join(tickers)}...")

# Load existing analysis data
aggregator = StockDataAggregator(current_date)
aggregated_result = aggregator.aggregate_multiple_stocks(tickers)

print(f"✅ Loaded {aggregated_result['num_stocks']} stock analyses")

# Manually create optimization scenarios (from the previous run)
optimization_scenarios = {
    'maximum_sharpe_ratio': {
        'method': 'Maximum Sharpe Ratio',
        'philosophy': 'Risk-Adjusted Return Maximization',
        'description': 'Maximizes risk-adjusted returns (Sharpe ratio)',
        'expected_return': 0.1325,
        'volatility': 0.4088,
        'sharpe_ratio': 0.295,
        'weights': {'NVDA': 0.6800, 'AAPL': 0.3200}
    },
    'minimum_variance': {
        'method': 'Minimum Variance',
        'philosophy': 'Risk Minimization',
        'description': 'Minimizes portfolio volatility',
        'expected_return': 0.1188,
        'volatility': 0.2372,
        'sharpe_ratio': 0.456,
        'weights': {'AAPL': 0.6988, 'NVDA': 0.3012}
    },
    'risk_parity': {
        'method': 'Risk Parity',
        'philosophy': 'Equal Risk Contribution',
        'description': 'Each asset contributes equally to portfolio risk',
        'expected_return': 0.1253,
        'volatility': 0.2890,
        'sharpe_ratio': 0.395,
        'weights': {'AAPL': 0.6163, 'NVDA': 0.3837}
    }
}

print(f"\n📊 Using {len(optimization_scenarios)} optimization scenarios")

print("\n" + "="*80)
print("Regenerating Portfolio Report with LLM Final Allocation")
print("="*80)

# Generate report with LLM integration
report_generator = PortfolioReportGenerator(
    aggregated_result,
    optimization_scenarios,
    current_date
)

try:
    report_path = report_generator.generate_comprehensive_report()
    print("\n" + "="*80)
    print("✅ REPORT REGENERATION COMPLETE")
    print("="*80)
    print(f"\n📄 Report saved to: {report_path}")
    print("\nPlease check Section 5 of the report to verify LLM Portfolio Manager decision!")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
