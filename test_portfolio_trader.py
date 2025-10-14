#!/usr/bin/env python3
"""
Test Portfolio Trader LLM Integration
"""

import os
import sys

# Set console encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Set environment variables
os.environ["WATSONX_APIKEY"] = "1NlP-L5h1DDEZFKkvJ92uTuMFNbkk0pmGJ4lMutJ44w2"
os.environ["WATSONX_PROJECT_ID"] = "394811a9-3e1c-4b80-8031-3fda71e6dce1"
os.environ["WATSONX_URL"] = "https://us-south.ml.cloud.ibm.com"

from tradingagents.portfolio.portfolio_trader import PortfolioTrader

# Test data - simplified version
aggregated_data = {
    'stocks_data': {
        'NVDA': {
            'metrics': {
                'current_price': 250.0,
                'expected_return': 44.1,
                'volatility': 49.7,
                'sharpe_ratio': 0.84,
                'technical_score': 7.0,
                'sentiment_score': 6.8,
                'rsi': 66
            },
            'risk_metrics': {
                'var_95': -3.0,
                'max_drawdown': -25.0,
                'annual_volatility': 49.7
            },
            'final_decision': 'HOLD',
            'fundamental_table': {
                'Revenue': '$28.3B',
                'Net Income': '$11.3B',
                'Profit Margin': '40%',
                'ROE': '35%'
            },
            'technical_table': {
                'RSI': '66',
                'MACD': 'Bullish',
                'SMA_20': '$245',
                'SMA_50': '$240'
            },
            'sentiment_analysis': {
                'overall_sentiment': 7.2,
                'bullish_count': 8,
                'bearish_count': 2,
                'sentiment_strength': 'Strong'
            }
        },
        'AAPL': {
            'metrics': {
                'current_price': 180.0,
                'expected_return': 35.0,
                'volatility': 28.0,
                'sharpe_ratio': 1.25,
                'technical_score': 7.0,
                'sentiment_score': 6.2,
                'rsi': 50
            },
            'risk_metrics': {
                'var_95': -3.0,
                'max_drawdown': -18.0,
                'annual_volatility': 28.0
            },
            'final_decision': 'HOLD',
            'fundamental_table': {
                'Revenue': '$385B',
                'Net Income': '$100B',
                'Profit Margin': '26%',
                'ROE': '160%'
            },
            'technical_table': {
                'RSI': '50',
                'MACD': 'Neutral',
                'SMA_20': '$178',
                'SMA_50': '$175'
            },
            'sentiment_analysis': {
                'overall_sentiment': 6.5,
                'bullish_count': 6,
                'bearish_count': 3,
                'sentiment_strength': 'Moderate'
            }
        }
    }
}

optimization_scenarios = {
    'maximum_sharpe_ratio': {
        'method': 'Maximum Sharpe Ratio',
        'philosophy': 'Risk-Adjusted Return Maximization',
        'description': 'Maximizes risk-adjusted returns (Sharpe ratio)',
        'expected_return': 0.8325,
        'volatility': 0.2720,
        'sharpe_ratio': 2.969,
        'weights': {'NVDA': 0.68, 'AAPL': 0.32}
    },
    'minimum_variance': {
        'method': 'Minimum Variance',
        'philosophy': 'Risk Minimization',
        'description': 'Minimizes portfolio volatility',
        'expected_return': 0.6188,
        'volatility': 0.2372,
        'sharpe_ratio': 2.503,
        'weights': {'AAPL': 0.6988, 'NVDA': 0.3012}
    },
    'risk_parity': {
        'method': 'Risk Parity',
        'philosophy': 'Equal Risk Contribution',
        'description': 'Each asset contributes equally to portfolio risk',
        'expected_return': 0.6653,
        'volatility': 0.2390,
        'sharpe_ratio': 2.680,
        'weights': {'AAPL': 0.6163, 'NVDA': 0.3837}
    }
}

market_context = "Current date: 2025-10-15, Market conditions: Moderate volatility tech environment"

print("="*80)
print("Testing Portfolio Trader with WatsonX LLM")
print("="*80)

try:
    print("\n1. Creating Portfolio Trader instance...")
    trader = PortfolioTrader(llm_provider="watsonx")
    print("   ✅ Portfolio Trader created successfully")

    print("\n2. Calling make_final_allocation...")
    result = trader.make_final_allocation(
        aggregated_data=aggregated_data,
        optimization_scenarios=optimization_scenarios,
        market_context=market_context
    )

    print("\n3. Result received:")
    print("="*80)

    if result and 'final_allocation' in result and result['final_allocation']:
        print("\n✅ SUCCESS! Final allocation:")
        for ticker, weight in result['final_allocation'].items():
            print(f"   - {ticker}: {weight*100:.2f}%")

        if 'rationale' in result:
            print(f"\n📝 Rationale:\n{result['rationale'][:500]}...")

        if 'confidence_level' in result:
            print(f"\n📊 Confidence Level: {result['confidence_level']}/10")

        if 'scenario_preference' in result:
            print(f"\n🎯 Preferred Scenario: {result['scenario_preference']}")
    else:
        print("\n❌ FAILED: No final allocation generated")
        print(f"Result: {result}")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
