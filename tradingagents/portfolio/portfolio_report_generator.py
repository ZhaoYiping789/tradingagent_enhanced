"""
Portfolio Report Generator
Creates comprehensive portfolio analysis reports with comparisons
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from datetime import datetime
from tradingagents.portfolio.portfolio_trader import PortfolioTrader


class PortfolioReportGenerator:
    """Generate comprehensive portfolio reports"""
    
    def __init__(self, aggregated_data: Dict, optimization_scenarios: Dict, date: str):
        self.aggregated_data = aggregated_data
        self.optimization_scenarios = optimization_scenarios
        self.date = date
        self.comparison_df = aggregated_data['comparison_df']
        
    def generate_comprehensive_report(self, output_dir: str = None) -> str:
        """Generate comprehensive portfolio report"""
        
        if output_dir is None:
            output_dir = f"portfolio_results/{self.date}"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate LLM final allocation decision
        portfolio_trader = PortfolioTrader()
        final_decision = portfolio_trader.make_final_allocation(
            aggregated_data=self.aggregated_data,
            optimization_scenarios=self.optimization_scenarios,
            market_context=f"Current date: {self.date}, Market conditions: Moderate volatility tech environment"
        )
        
        # Generate Markdown report with LLM decision
        md_report = self._create_markdown_report(final_decision)
        
        # Save Markdown
        md_path = output_path / f"portfolio_analysis_{self.date}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_report)
        
        print(f"Portfolio report saved to: {md_path}")
        return str(md_path)
    
    def _create_markdown_report(self, final_decision: Dict = None) -> str:
        """Create comprehensive markdown report"""
        
        report = f"""# Multi-Stock Portfolio Analysis Report
**Date:** {self.date}

---

## SECTION 1: INDIVIDUAL STOCK COMPARISON

### Technical Analysis Comparison

| Ticker | Decision | Expected Return | Volatility | Sharpe Ratio | RSI | Technical Score | Sentiment Score |
|--------|----------|-----------------|------------|--------------|-----|-----------------|-----------------|
"""
        
        # Add stock comparison rows
        for _, row in self.comparison_df.iterrows():
            report += f"| **{row['Ticker']}** | {row['Decision']} | {row['Expected Return']:.1f}% | {row['Volatility']:.1f}% | {row['Sharpe Ratio']:.2f} | {row['RSI']:.0f} | {row['Technical Score']:.1f}/10 | {row['Sentiment Score']:.1f}/10 |\n"
        
        report += """

### Risk Metrics Comparison

| Ticker | VaR 95% | Max Drawdown | Current Price |
|--------|---------|--------------|---------------|
"""
        
        for _, row in self.comparison_df.iterrows():
            report += f"| **{row['Ticker']}** | {row['VaR 95%']:.2f}% | {row['Max Drawdown']:.1f}% | ${row['Current Price']:.2f} |\n"
        
        report += """

### Individual Stock Analysis Summary

"""
        
        for ticker in self.comparison_df['Ticker']:
            row = self.comparison_df[self.comparison_df['Ticker'] == ticker].iloc[0]
            
            # Determine sentiment
            if row['Technical Score'] >= 7:
                technical_sentiment = "BULLISH"
            elif row['Technical Score'] <= 4:
                technical_sentiment = "BEARISH"
            else:
                technical_sentiment = "NEUTRAL"
            
            report += f"""**{ticker}:**
- **Decision:** {row['Decision']}
- **Technical Sentiment:** {technical_sentiment} (Score: {row['Technical Score']:.1f}/10)
- **Expected Annual Return:** {row['Expected Return']:.1f}%
- **Volatility:** {row['Volatility']:.1f}% ({"High" if row['Volatility'] > 35 else "Moderate" if row['Volatility'] > 20 else "Low"} risk)
- **Sharpe Ratio:** {row['Sharpe Ratio']:.2f}
- **Key Insight:** {"Strong momentum with high returns" if row['Expected Return'] > 40 else "Stable moderate growth" if row['Expected Return'] > 15 else "Conservative profile"}

"""
        
        report += """---

## SECTION 2: PORTFOLIO OPTIMIZATION SCENARIOS

We tested 6 different portfolio construction strategies:

### Optimization Scenarios Comparison

| Strategy | Philosophy | Expected Return | Volatility | Sharpe Ratio | Top Holdings |
|----------|------------|-----------------|------------|--------------|--------------|
"""
        
        for scenario_name, scenario_data in self.optimization_scenarios.items():
            # Get top 2 holdings
            weights_sorted = sorted(scenario_data['weights'].items(), key=lambda x: x[1], reverse=True)
            top_holdings = f"{weights_sorted[0][0]} ({weights_sorted[0][1]*100:.2f}%), {weights_sorted[1][0]} ({weights_sorted[1][1]*100:.2f}%)"
            
            report += f"| **{scenario_data['method']}** | {scenario_data['philosophy']} | {scenario_data['expected_return']*100:.2f}% | {scenario_data['volatility']*100:.2f}% | {scenario_data['sharpe_ratio']:.3f} | {top_holdings} |\n"
        
        report += """

### Detailed Scenario Analysis

"""
        
        for scenario_name, scenario_data in self.optimization_scenarios.items():
            report += f"""#### {scenario_data['method']}
- **Philosophy:** {scenario_data['philosophy']}
- **Description:** {scenario_data['description']}
- **Expected Return:** {scenario_data['expected_return']*100:.2f}%
- **Volatility:** {scenario_data['volatility']*100:.2f}%
- **Sharpe Ratio:** {scenario_data['sharpe_ratio']:.3f}

**Allocation:**
"""
            
            for ticker, weight in sorted(scenario_data['weights'].items(), key=lambda x: x[1], reverse=True):
                report += f"- {ticker}: {weight*100:.2f}%\n"
            
            report += "\n"
        
        report += """---

## SECTION 3: PORTFOLIO RECOMMENDATIONS

### Scenario Selection Guide

Choose based on your investment philosophy:

1. **Conservative Investor (Risk-Averse):**
   - Recommended: **Minimum Variance** or **Maximum Diversification**
   - Focus: Stability and capital preservation
   - Typical volatility: 20-25%

2. **Balanced Investor (Moderate Risk):**
   - Recommended: **Risk Parity** or **Hierarchical Risk Parity**
   - Focus: Balance between growth and stability
   - Typical volatility: 25-30%

3. **Aggressive Investor (Growth-Focused):**
   - Recommended: **Maximum Sharpe Ratio**
   - Focus: Maximize risk-adjusted returns
   - Typical volatility: 30-35%

4. **Diversification-Focused:**
   - Recommended: **Maximum Diversification** or **HRP**
   - Focus: Reduce concentration risk
   - Well-balanced across all stocks

### Portfolio Metrics Summary

| Metric | Min | Max | Average |
|--------|-----|-----|---------|
"""
        
        # Get metrics from optimization scenarios, with fallback to individual stock data
        if self.optimization_scenarios and len(self.optimization_scenarios) > 0:
            returns = [s['expected_return']*100 for s in self.optimization_scenarios.values() if 'expected_return' in s]
            vols = [s['volatility']*100 for s in self.optimization_scenarios.values() if 'volatility' in s]
            sharpes = [s['sharpe_ratio'] for s in self.optimization_scenarios.values() if 'sharpe_ratio' in s]
        else:
            # Fallback: use individual stock metrics
            stock_data = self.aggregated_data['stocks_data']
            returns = [data['metrics']['expected_return'] for data in stock_data.values()]
            vols = [data['metrics']['volatility'] for data in stock_data.values()]
            sharpes = [data['metrics']['sharpe_ratio'] for data in stock_data.values()]
        
        # Only add metrics if we have data
        if returns and vols and sharpes:
            report += f"| Expected Return | {min(returns):.1f}% | {max(returns):.1f}% | {np.mean(returns):.1f}% |\n"
            report += f"| Volatility | {min(vols):.1f}% | {max(vols):.1f}% | {np.mean(vols):.1f}% |\n"
            report += f"| Sharpe Ratio | {min(sharpes):.2f} | {max(sharpes):.2f} | {np.mean(sharpes):.2f} |\n"
        else:
            report += "| Expected Return | N/A | N/A | N/A |\n"
            report += "| Volatility | N/A | N/A | N/A |\n"
            report += "| Sharpe Ratio | N/A | N/A | N/A |\n"
        
        report += """

---

## SECTION 4: CORRELATION AND DIVERSIFICATION ANALYSIS

### Stock Correlation Insights

"""
        
        # Calculate correlation insights
        report += self._generate_correlation_insights()
        
        report += """

---

## SECTION 5: FINAL PORTFOLIO ALLOCATION

### Institutional Portfolio Manager Decision

"""
        
        # Add detailed LLM analysis with raw data integration
        if final_decision and 'final_allocation' in final_decision and final_decision['final_allocation']:
            
            # 1. Show all algorithm recommendations first
            report += "### Optimization Algorithms Summary\n\n"
            report += "| Algorithm | Philosophy | NVDA Weight | AAPL Weight | Key Insight |\n"
            report += "|-----------|------------|-------------|-------------|-------------|\n"
            
            for scenario_name, scenario_data in self.optimization_scenarios.items():
                if 'weights' in scenario_data:
                    nvda_weight = scenario_data['weights'].get('NVDA', 0) * 100
                    aapl_weight = scenario_data['weights'].get('AAPL', 0) * 100
                    philosophy = scenario_data.get('philosophy', 'N/A')
                    
                    # Color code based on concentration
                    if max(nvda_weight, aapl_weight) > 70:
                        insight = "HIGH CONCENTRATION"
                    elif abs(nvda_weight - aapl_weight) < 20:
                        insight = "BALANCED"
                    else:
                        insight = "MODERATE TILT"
                    
                    report += f"| {scenario_name.replace('_', ' ').title()} | {philosophy} | {nvda_weight:.2f}% | {aapl_weight:.2f}% | {insight} |\n"
            
            report += "\n### Raw Data Analysis Integration\n\n"
            
            # 2. Show raw fundamental comparison
            report += "**📊 FUNDAMENTAL ANALYSIS RAW DATA:**\n\n"
            report += "| Metric | NVDA | AAPL | Comparison |\n"
            report += "|--------|------|------|------------|\n"
            
            nvda_data = self.aggregated_data['stocks_data']['NVDA']
            aapl_data = self.aggregated_data['stocks_data']['AAPL']
            
            # Compare key metrics with color coding
            metrics_comparison = [
                ("Expected Return", nvda_data['metrics']['expected_return'], aapl_data['metrics']['expected_return'], "%"),
                ("Volatility", nvda_data['metrics']['volatility'], aapl_data['metrics']['volatility'], "%"),
                ("Current Price", nvda_data['metrics']['current_price'], aapl_data['metrics']['current_price'], "$"),
                ("Technical Score", nvda_data['metrics']['technical_score'], aapl_data['metrics']['technical_score'], "/10"),
            ]
            
            for metric_name, nvda_val, aapl_val, unit in metrics_comparison:
                if metric_name == "Expected Return":
                    nvda_color = "HIGH" if nvda_val > aapl_val else "MED"
                    aapl_color = "HIGH" if aapl_val > nvda_val else "MED"  
                    comparison = "NVDA ADVANTAGE" if nvda_val > aapl_val else "AAPL ADVANTAGE"
                elif metric_name == "Volatility":
                    nvda_color = "HIGH" if nvda_val > aapl_val else "LOW"
                    aapl_color = "HIGH" if aapl_val > nvda_val else "LOW"
                    comparison = "AAPL LOWER RISK" if aapl_val < nvda_val else "NVDA LOWER RISK"
                else:
                    nvda_color = aapl_color = "MED"
                    comparison = "SIMILAR"
                
                if unit == "$":
                    report += f"| {metric_name} | {nvda_color} ${nvda_val:.2f} | {aapl_color} ${aapl_val:.2f} | {comparison} |\n"
                else:
                    report += f"| {metric_name} | {nvda_color} {nvda_val:.2f}{unit} | {aapl_color} {aapl_val:.2f}{unit} | {comparison} |\n"
            
            # Add sentiment analysis comparison if available
            if nvda_data.get('sentiment_analysis') and aapl_data.get('sentiment_analysis'):
                report += "\n**SENTIMENT ANALYSIS RAW DATA:**\n\n"
                report += "| Metric | NVDA | AAPL | Analysis |\n"
                report += "|--------|------|------|---------|\n"
                
                nvda_sentiment = nvda_data['sentiment_analysis']
                aapl_sentiment = aapl_data['sentiment_analysis']
                
                # Sentiment Score
                nvda_score = nvda_sentiment['overall_sentiment']
                aapl_score = aapl_sentiment['overall_sentiment']
                nvda_label = "BULLISH" if nvda_score > 6.5 else "BEARISH" if nvda_score < 3.5 else "NEUTRAL"
                aapl_label = "BULLISH" if aapl_score > 6.5 else "BEARISH" if aapl_score < 3.5 else "NEUTRAL"
                
                report += f"| Overall Sentiment | {nvda_label} ({nvda_score:.1f}/10) | {aapl_label} ({aapl_score:.1f}/10) | {'NVDA MORE POSITIVE' if nvda_score > aapl_score else 'AAPL MORE POSITIVE' if aapl_score > nvda_score else 'SIMILAR SENTIMENT'} |\n"
                
                # Sentiment Counts
                nvda_bullish = nvda_sentiment.get('bullish_count', 0)
                aapl_bullish = aapl_sentiment.get('bullish_count', 0)
                report += f"| Bullish Mentions | {nvda_bullish} mentions | {aapl_bullish} mentions | {'NVDA MORE BUZZ' if nvda_bullish > aapl_bullish else 'AAPL MORE BUZZ' if aapl_bullish > nvda_bullish else 'SIMILAR COVERAGE'} |\n"
                
                nvda_bearish = nvda_sentiment.get('bearish_count', 0)
                aapl_bearish = aapl_sentiment.get('bearish_count', 0)
                report += f"| Bearish Mentions | {nvda_bearish} mentions | {aapl_bearish} mentions | {'NVDA MORE CONCERNS' if nvda_bearish > aapl_bearish else 'AAPL MORE CONCERNS' if aapl_bearish > nvda_bearish else 'SIMILAR CONCERNS'} |\n"
                
                # Sentiment Strength
                nvda_strength = nvda_sentiment.get('sentiment_strength', 'Weak')
                aapl_strength = aapl_sentiment.get('sentiment_strength', 'Weak')
                report += f"| Sentiment Strength | {nvda_strength} | {aapl_strength} | Confidence in sentiment signals |\n"
            
            report += "\n**FINAL RECOMMENDED ALLOCATION:**\n\n"
            
            total_allocation = sum(final_decision['final_allocation'].values())
            for ticker, weight in sorted(final_decision['final_allocation'].items(), key=lambda x: x[1], reverse=True):
                percentage = weight * 100 if total_allocation <= 1.1 else weight  # Handle decimal vs percentage
                report += f"- **{ticker}**: {percentage:.2f}%\n"
            
            report += f"\n**Portfolio Manager Detailed Analysis:**\n{final_decision.get('rationale', 'No rationale provided')}\n\n"
            
            if 'confidence_level' in final_decision:
                report += f"**Confidence Level:** {final_decision['confidence_level']}/10\n"
            if 'time_horizon' in final_decision:
                report += f"**Time Horizon:** {final_decision['time_horizon']}\n"
            if 'scenario_preference' in final_decision:
                report += f"**Preferred Optimization Approach:** {final_decision['scenario_preference']}\n\n"
                
            if 'key_factors' in final_decision and final_decision['key_factors']:
                report += "**Key Decision Factors:**\n"
                for factor in final_decision['key_factors']:
                    report += f"- {factor}\n"
        else:
            report += "**Portfolio Manager Analysis:** *LLM analysis not available*\n\n"
            report += "The LLM portfolio manager will integrate these optimization scenarios with:\n"
            report += "- Individual stock analysis (fundamentals, technicals, sentiment)\n"
            report += "- Market conditions and sector trends\n"
            report += "- Correlation and diversification benefits\n"
            report += "- Risk tolerance and investment horizon\n\n"
            report += "**Note:** Final allocation decision requires LLM integration.\n"

        report += "\n---\n\n"
        report += "*Report generated by TradingAgents Portfolio Analysis System*\n"
        report += "*For informational purposes only - not financial advice*\n"
        
        return report
    
    def _generate_correlation_insights(self) -> str:
        """Generate correlation analysis insights"""
        
        insights = ""
        
        tickers = self.comparison_df['Ticker'].tolist()
        
        if len(tickers) < 2:
            return "Insufficient stocks for correlation analysis.\n"
        
        insights += f"Portfolio contains {len(tickers)} stocks.\n\n"
        insights += "**Diversification Benefits:**\n"
        insights += f"- Portfolio spans {len(set([t[:2] for t in tickers]))} sectors\n"
        insights += f"- Average correlation expected: 0.60-0.80 (tech stocks)\n"
        insights += "- Diversification ratio: Higher is better\n"
        
        return insights
