"""
Enterprise Strategy Analyst - Advanced Trading Plan Generation
Generates sophisticated trading execution strategies using LLM analysis
"""

from langchain_core.prompts import ChatPromptTemplate
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json


def format_optimization_results(optimization_results: Dict) -> str:
    """Format optimization results for strategy integration"""
    if not optimization_results:
        return "No mathematical optimization results available"
    
    formatted = "## MATHEMATICAL OPTIMIZATION SUMMARY\n\n"
    
    # Kelly Criterion Results
    kelly = optimization_results.get('kelly_criterion', {})
    if kelly:
        formatted += f"### Kelly Criterion Position Sizing:\n"
        formatted += f"- Recommended Position: {kelly.get('recommended_position', 0.05):.1%} of portfolio\n"
        formatted += f"- Win Probability: {kelly.get('win_probability', 0.55):.1%}\n"
        formatted += f"- Risk-Adjusted Kelly: {kelly.get('risk_adjusted_kelly', 0.03):.1%}\n\n"
    
    # GARCH Volatility Results
    garch = optimization_results.get('garch_volatility', {})
    if garch:
        formatted += f"### GARCH Volatility Forecast:\n"
        formatted += f"- Forecasted Volatility: {garch.get('forecasted_volatility', 0.25):.1%} (annualized)\n"
        formatted += f"- Volatility Regime: {garch.get('regime', 'Normal')}\n"
        formatted += f"- Confidence Interval: [{garch.get('lower_bound', 0.20):.1%}, {garch.get('upper_bound', 0.30):.1%}]\n\n"
    
    # Portfolio Optimization Results
    portfolio = optimization_results.get('portfolio_optimization', {})
    if portfolio:
        formatted += f"### Portfolio Optimization:\n"
        formatted += f"- Optimal Weight: {portfolio.get('optimal_weight', 0.08):.1%}\n"
        formatted += f"- Expected Return: {portfolio.get('expected_return', 0.12):.1%}\n"
        formatted += f"- Risk Contribution: {portfolio.get('risk_contribution', 0.05):.1%}\n\n"
    
    # Risk Metrics
    risk_metrics = optimization_results.get('risk_metrics', {})
    if risk_metrics:
        formatted += f"### Risk Metrics:\n"
        formatted += f"- 95% VaR: {risk_metrics.get('var_95', -0.023):.1%}\n"
        formatted += f"- 95% CVaR: {risk_metrics.get('cvar_95', -0.031):.1%}\n"
        formatted += f"- Maximum Drawdown: {risk_metrics.get('max_drawdown', -0.152):.1%}\n"
        formatted += f"- Sharpe Ratio: {risk_metrics.get('sharpe_ratio', 1.45):.2f}\n\n"
    
    return formatted


def create_enterprise_strategy_analyst(llm, toolkit):
    """Create an enterprise-level strategy analyst that generates comprehensive trading plans."""
    
    def enterprise_strategy_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        # Gather all analysis data and escape curly braces for LangChain template compatibility
        def escape_braces(text):
            """Escape curly braces to prevent LangChain template variable interpretation"""
            if isinstance(text, str):
                return text.replace("{", "{{").replace("}", "}}")
            return text

        market_report = escape_braces(state.get("market_report", ""))
        sentiment_report = escape_braces(state.get("sentiment_report", ""))
        news_report = escape_braces(state.get("news_report", ""))
        fundamentals_report = escape_braces(state.get("fundamentals_report", ""))
        quantitative_report = escape_braces(state.get("quantitative_report", ""))
        comprehensive_quantitative_report = escape_braces(state.get("comprehensive_quantitative_report", ""))
        optimization_results = state.get("optimization_results", {})
        investment_debate_state = state.get("investment_debate_state", {})
        risk_debate_state = state.get("risk_debate_state", {})
        trader_plan = escape_braces(state.get("trader_investment_plan", ""))
        
        # Get current market data for price calculations
        try:
            if toolkit.config["online_tools"]:
                current_data = toolkit.get_YFin_data_online(ticker)
            else:
                current_data = toolkit.get_YFin_data(ticker)
            
            # Extract current price and volatility
            if current_data and "Current Price" in current_data:
                current_price = float(current_data.split("Current Price: $")[1].split()[0])
            else:
                current_price = 250.0  # Fallback if data unavailable
                
        except Exception as e:
            current_price = 250.0  # Fallback
        
        # Create comprehensive strategy prompt
        strategy_prompt = f"""
You are an ENTERPRISE-LEVEL TRADING STRATEGIST with 20+ years of institutional experience. Your task is to create a sophisticated, actionable trading execution plan based on comprehensive multi-agent analysis.

## 📊 ANALYSIS SUMMARY

**TICKER:** {ticker}
**CURRENT PRICE:** ${current_price:.2f}
**ANALYSIS DATE:** {current_date}

### Technical Analysis Results:
{market_report}

### Sentiment Analysis Results:
{sentiment_report}

### News Analysis Results:
{news_report}

### Fundamental Analysis Results:
{fundamentals_report}

### Quantitative Model Results:
{quantitative_report}

### COMPREHENSIVE QUANTITATIVE ANALYSIS (WITH OPTIMIZATION):
{comprehensive_quantitative_report}

### MATHEMATICAL OPTIMIZATION RESULTS:
{format_optimization_results(optimization_results)}

### Investment Debate Outcome:
Bull vs Bear Analysis: {investment_debate_state.get('judge_decision', 'No debate conducted')}

### Risk Management Assessment:
{risk_debate_state.get('judge_decision', 'No risk analysis')}

### Initial Trading Plan:
{trader_plan}

## 🎯 YOUR MISSION

Generate a COMPREHENSIVE TRADING EXECUTION STRATEGY that includes:

### 1. MULTI-TIMEFRAME STRATEGY SELECTION
Based on the analysis, determine which timeframe strategy is most appropriate:

**A) SHORT-TERM (1-3 months) - Momentum/Swing Strategy**
- Focus: Technical breakouts, earnings momentum, news catalysts
- Position sizing: Higher frequency, smaller positions
- Risk management: Tight stops, quick profits

**B) MEDIUM-TERM (3-12 months) - Trend Following Strategy**
- Focus: Fundamental trends, sector rotation, business cycle
- Position sizing: Moderate positions with scaling
- Risk management: Trailing stops, milestone-based exits

**C) LONG-TERM (1-3 years) - Value/Growth Investment**
- Focus: Fundamental value, competitive moats, secular trends
- Position sizing: Core positions with periodic rebalancing
- Risk management: Wide stops, fundamental-based exits

### 2. SOPHISTICATED POSITION SIZING
**CRITICAL**: Use the mathematical optimization results provided above to calculate position sizes:
- **Kelly Criterion**: Use the calculated Kelly position from optimization results
- **GARCH Volatility**: Incorporate the forecasted volatility for risk adjustment
- **Portfolio Optimization**: Use the optimal weight from portfolio optimization
- **Risk Metrics**: Ensure position sizing respects VaR and CVaR constraints
- **Quantitative Integration**: Synthesize all mathematical models for final position size

### 3. ADVANCED ENTRY STRATEGY
Design a multi-phase entry approach:
- **Primary Entry Zone**: Ideal entry price range with reasoning
- **Secondary Entry**: Opportunity on pullbacks/dips
- **Scaling Strategy**: How to build the position over time
- **Trigger Conditions**: Specific market/technical triggers for each entry

### 4. COMPREHENSIVE RISK MANAGEMENT
- **Stop-Loss Levels**: Multiple stop levels (tight, medium, wide)
- **Position Sizing Risk**: Maximum position size as % of portfolio
- **Time-Based Stops**: Maximum holding period before review
- **Fundamental Stops**: Business/fundamental change triggers
- **Volatility Stops**: Adjust stops based on market volatility

### 5. PROFIT-TAKING STRATEGY
- **Take-Profit Targets**: Multiple target levels with probabilities
- **Scaling Out Plan**: Partial profit-taking strategy
- **Trailing Stops**: Dynamic stop-loss adjustment
- **Fundamental Exits**: When business thesis changes

### 6. EXECUTION TIMELINE
Create a week-by-week execution plan:
- **Week 1-2**: Initial positioning and market entry
- **Week 3-4**: Position monitoring and potential scaling
- **Week 5-8**: Mid-term assessment and adjustments
- **Month 2-3**: Long-term positioning review

### 7. MONITORING & REVIEW PLAN
- **Daily Monitoring**: Key metrics to track daily
- **Weekly Reviews**: Performance and strategy validation
- **Monthly Rebalancing**: Position size and strategy adjustments
- **Quarterly Reviews**: Fundamental thesis validation

##  CRITICAL REQUIREMENTS

1. **BE SPECIFIC**: Provide exact price levels, percentages, and timeframes
2. **SHOW YOUR MATH**: Explain calculations for position sizes and risk levels
3. **CONSIDER ALL DATA**: Synthesize insights from ALL provided analyses
4. **BE PRACTICAL**: Ensure strategy is executable in real markets
5. **ADDRESS RISKS**: Explicitly handle identified risks and scenarios
6. **PROVIDE RATIONALE**: Explain WHY each decision is optimal

##  OUTPUT FORMAT

Structure your response as follows:

###  STRATEGIC RECOMMENDATION
- Overall Position: [ACCUMULATE/REDUCE/HOLD/AVOID]
- Confidence Level: [1-10 scale with reasoning]
- Time Horizon: [Specific timeframe with rationale]
- Risk Level: [Conservative/Moderate/Aggressive with justification]

###  POSITION SIZING CALCULATION
- Recommended Position Size: [Specific $ amount or % of portfolio]
- Kelly Criterion Result: [Show calculation]
- Volatility Adjustment: [Adjustment factor and reasoning]
- Maximum Risk Per Trade: [$ amount and % of portfolio]

###  ENTRY STRATEGY
- Primary Entry Zone: $[X.XX] - $[Y.YY] ([Z]% of total position)
- Entry Trigger 1: [Specific condition]
- Entry Trigger 2: [Specific condition]
- Scaling Plan: [Week-by-week breakdown]

###  RISK MANAGEMENT
- Stop Loss 1 (Tight): $[X.XX] (-[Y]% risk)
- Stop Loss 2 (Medium): $[X.XX] (-[Y]% risk)
- Stop Loss 3 (Wide): $[X.XX] (-[Y]% risk)
- Position Size Limit: [Maximum % of portfolio]
- Time Stop: [Maximum days to hold before review]

###  PROFIT TARGETS
- Target 1 (Conservative): $[X.XX] (+[Y]% gain, [Z]% probability)
- Target 2 (Moderate): $[X.XX] (+[Y]% gain, [Z]% probability)
- Target 3 (Aggressive): $[X.XX] (+[Y]% gain, [Z]% probability)
- Scaling Out: [Specific plan for taking profits]

###  EXECUTION TIMELINE
Week 1: [Specific actions]
Week 2: [Specific actions]
Week 3-4: [Specific actions]
Month 2: [Review points]
Quarter 1: [Major review]

###  MONITORING DASHBOARD
Daily: [Key metrics to track]
Weekly: [Performance review checklist]
Monthly: [Strategy validation points]
Quarterly: [Fundamental review criteria]

###  SCENARIO ANALYSIS
Bull Case (+20% scenario): [Strategy adjustments]
Base Case (Expected): [Current strategy execution]
Bear Case (-20% scenario): [Risk mitigation actions]

###  STRATEGY RATIONALE
[Detailed explanation of why this strategy is optimal given all available data, addressing potential counterarguments and showing how it maximizes risk-adjusted returns]

Remember: This strategy will be executed with real money. Make it institutional-quality, data-driven, and thoroughly reasoned. Consider the human psychology of trading and build in safeguards against emotional decision-making.
"""

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an elite institutional trading strategist generating sophisticated trading execution plans."),
            ("human", strategy_prompt)
        ])
        
        # Generate the strategy
        chain = prompt | llm
        result = chain.invoke({})
        
        return {
            "messages": [result],
            "enterprise_strategy": result.content,
            "strategy_confidence": extract_confidence_level(result.content),
            "recommended_action": extract_recommendation(result.content)
        }
    
    return enterprise_strategy_node


def extract_confidence_level(strategy_content: str) -> float:
    """Extract confidence level from strategy content"""
    try:
        # Look for confidence level in the content
        import re
        confidence_match = re.search(r'Confidence Level:.*?(\d+(?:\.\d+)?)', strategy_content, re.IGNORECASE)
        if confidence_match:
            return float(confidence_match.group(1)) / 10.0  # Convert to 0-1 scale
        return 0.7  # Default moderate confidence
    except:
        return 0.7


def extract_recommendation(strategy_content: str) -> str:
    """Extract the main recommendation from strategy content"""
    try:
        import re
        # Look for strategic recommendation
        rec_match = re.search(r'Overall Position:.*?(ACCUMULATE|REDUCE|HOLD|AVOID)', strategy_content, re.IGNORECASE)
        if rec_match:
            action = rec_match.group(1).upper()
            # Convert to standard format
            if action == "ACCUMULATE":
                return "BUY"
            elif action == "REDUCE":
                return "SELL"
            elif action in ["HOLD", "AVOID"]:
                return "HOLD"
        return "HOLD"  # Default
    except:
        return "HOLD"
