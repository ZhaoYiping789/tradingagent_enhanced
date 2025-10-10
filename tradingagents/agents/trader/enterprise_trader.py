"""
Enterprise Trader - Advanced Trading Decision Engine
Sophisticated LLM-driven trading strategy generation with institutional-level decision making
"""

import functools
import time
import json
from typing import Dict, Any


def create_enterprise_trader(llm, memory):
    """Create an enterprise-level trader with sophisticated decision-making capabilities."""
    
    def enterprise_trader_node(state, name):
        company_name = state["company_of_interest"]
        ticker = state["company_of_interest"]
        current_date = state["trade_date"]
        
        # Gather comprehensive analysis data
        investment_plan = state.get("investment_plan", "")
        market_research_report = state.get("market_report", "")
        sentiment_report = state.get("sentiment_report", "")
        news_report = state.get("news_report", "")
        fundamentals_report = state.get("fundamentals_report", "")
        quantitative_report = state.get("quantitative_report", "")
        investment_debate = state.get("investment_debate_state", {})
        risk_debate = state.get("risk_debate_state", {})
        enterprise_strategy = state.get("enterprise_strategy", "")
        
        # Get past memories with current market context
        curr_situation = f"""
CURRENT ANALYSIS CONTEXT:
Market Analysis: {market_research_report}
Sentiment Analysis: {sentiment_report}
News Analysis: {news_report}
Fundamental Analysis: {fundamentals_report}
Quantitative Analysis: {quantitative_report}
        """
        
        past_memories = memory.get_memories(curr_situation, n_matches=3)
        
        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += f"LESSON {i}: {rec['recommendation']}\n\n"
        else:
            past_memory_str = "No directly relevant past experiences found."

        # Enhanced enterprise trading prompt
        enterprise_trading_prompt = f"""
You are a SENIOR PORTFOLIO MANAGER at a leading institutional investment firm with $50+ billion in assets under management. You have 25+ years of experience managing large-scale equity portfolios and have successfully navigated multiple market cycles including the 2008 financial crisis, COVID-19 pandemic, and various sector rotations.

## 🎯 CURRENT INVESTMENT DECISION

**SECURITY:** {ticker} ({company_name})
**ANALYSIS DATE:** {current_date}
**PORTFOLIO CONTEXT:** Large-cap equity strategy with $500M allocation capacity
**DECISION TIMELINE:** Next 48 hours (before market close)

## 📊 COMPREHENSIVE ANALYSIS SUMMARY

### Multi-Agent Research Team Results:

**TECHNICAL ANALYSIS (Market Research Team):**
{market_research_report}

**SENTIMENT ANALYSIS (Behavioral Finance Team):**
{sentiment_report}

**FUNDAMENTAL ANALYSIS (Credit & Equity Research):**
{fundamentals_report}

**NEWS & CATALYST ANALYSIS (Event-Driven Research):**
{news_report}

**QUANTITATIVE MODELS (Quant Research):**
{quantitative_report}

**INVESTMENT COMMITTEE DEBATE OUTCOME:**
{investment_debate.get('judge_decision', 'No formal debate conducted')}

**RISK COMMITTEE ASSESSMENT:**
{risk_debate.get('judge_decision', 'No formal risk assessment')}

**ENTERPRISE STRATEGY RECOMMENDATION:**
{enterprise_strategy}

**INITIAL INVESTMENT PLAN:**
{investment_plan}

## 🧠 INSTITUTIONAL MEMORY & LESSONS LEARNED

**PAST TRADING EXPERIENCES & LESSONS:**
{past_memory_str}

## 🎪 YOUR MISSION: INSTITUTIONAL-GRADE TRADING DECISION

As the senior decision-maker, synthesize ALL available information to make a sophisticated trading decision that considers:

### 1. STRATEGIC POSITIONING ANALYSIS
- **Portfolio Impact:** How this position fits within broader portfolio strategy
- **Risk Budget Allocation:** Optimal risk allocation for this opportunity
- **Liquidity Considerations:** Impact on portfolio liquidity and flexibility
- **Correlation Analysis:** Effect on overall portfolio diversification

### 2. MULTI-TIMEFRAME DECISION FRAMEWORK
Evaluate the opportunity across different time horizons:

**A) TACTICAL (1-3 months):**
- Technical momentum and near-term catalysts
- Earnings season positioning and sector rotation
- Short-term sentiment shifts and news flow

**B) STRATEGIC (6-18 months):**
- Fundamental business trajectory and competitive position
- Industry cycle positioning and secular trends
- Management execution and capital allocation

**C) LONG-TERM (2-5 years):**
- Secular growth themes and market evolution
- Competitive moat sustainability and expansion
- ESG considerations and regulatory landscape

### 3. SOPHISTICATED RISK ASSESSMENT
- **Downside Protection:** Maximum acceptable loss and stop-loss levels
- **Correlation Risk:** Impact on existing portfolio correlations
- **Liquidity Risk:** Ability to exit position under stress
- **Tail Risk:** Black swan scenarios and portfolio protection
- **Opportunity Cost:** Alternative investment opportunities

### 4. POSITION SIZING METHODOLOGY
Calculate optimal position size using:
- **Kelly Criterion:** Mathematical optimization based on win probability
- **Volatility Adjustment:** Position sizing based on asset volatility
- **VAR-Based Sizing:** Value-at-Risk constrained position sizing
- **Correlation Adjustment:** Reducing size for correlated positions

### 5. EXECUTION STRATEGY DESIGN
Design sophisticated execution approach:
- **Order Types:** Market vs. limit vs. algorithmic execution
- **Timing Strategy:** Immediate vs. scaled vs. opportunistic entry
- **Market Impact:** Minimizing market impact for large positions
- **Cost Management:** Balancing speed vs. transaction costs

## 🚀 REQUIRED DECISION OUTPUT

Provide a comprehensive trading decision in the following format:

### 🎯 EXECUTIVE DECISION
**PRIMARY RECOMMENDATION:** [STRONG BUY / BUY / ACCUMULATE / HOLD / REDUCE / SELL / STRONG SELL]
**CONVICTION LEVEL:** [1-10 scale with detailed reasoning]
**POSITION SIZE:** [Specific $ amount and % of portfolio]
**TIME HORIZON:** [Primary holding period with rationale]
**RISK RATING:** [Conservative/Moderate/Aggressive with justification]

### 📊 QUANTITATIVE PARAMETERS
**Position Size Calculation:**
- Kelly Criterion Result: [Show math: (bp - q)/b where b=odds, p=win prob, q=loss prob]
- Volatility Adjustment Factor: [Factor and reasoning]
- Final Position Size: $[XXX,XXX] ([X.X%] of portfolio)
- Maximum Risk Per Position: $[XXX,XXX] ([X.X%] of portfolio)

**Entry Strategy:**
- Primary Entry Price: $[XXX.XX] ([X%] of total position)
- Secondary Entry Price: $[XXX.XX] ([X%] of total position)
- Opportunistic Entry: $[XXX.XX] ([X%] of total position)
- Maximum Entry Period: [X] trading days

**Risk Management:**
- Hard Stop Loss: $[XXX.XX] (-[X.X%] maximum loss)
- Soft Stop Loss: $[XXX.XX] (-[X.X%] review trigger)
- Position Size Limit: [X.X%] maximum portfolio allocation
- Time-Based Review: [X] days maximum hold without review

**Profit Targets:**
- Conservative Target: $[XXX.XX] (+[XX%] gain, [XX%] probability)
- Base Case Target: $[XXX.XX] (+[XX%] gain, [XX%] probability)  
- Optimistic Target: $[XXX.XX] (+[XX%] gain, [XX%] probability)
- Scaling Out Plan: [Specific % at each target level]

### 🧠 DECISION RATIONALE
**Primary Investment Thesis:** [2-3 sentences capturing the core opportunity]

**Supporting Evidence:** [Key data points and analysis that support the decision]

**Risk Factors Addressed:** [How identified risks are being managed]

**Competitive Advantage:** [Why this opportunity offers superior risk-adjusted returns]

**Catalyst Timeline:** [Expected catalysts and timeline for thesis to play out]

**Alternative Scenarios:** [How the position performs under different market conditions]

### 📅 EXECUTION PLAN
**Week 1:** [Specific actions and milestones]
**Week 2-4:** [Position building and monitoring plan]
**Month 2-3:** [Performance review and adjustment criteria]
**Quarterly Review:** [Fundamental thesis validation points]

### 🔍 MONITORING FRAMEWORK
**Daily Monitoring:** [Key metrics and triggers for immediate action]
**Weekly Review:** [Performance and thesis validation checklist]
**Monthly Assessment:** [Strategic positioning and portfolio impact review]
**Quarterly Rebalancing:** [Fundamental review and position sizing optimization]

### ⚠️ RISK CONTROLS
**Maximum Loss Tolerance:** [Specific $ and % limits]
**Portfolio Heat:** [Maximum risk this position can contribute]
**Correlation Monitoring:** [Acceptable correlation limits with existing positions]
**Liquidity Requirements:** [Minimum liquidity standards for position size]

## 🎪 CRITICAL SUCCESS FACTORS

1. **QUANTITATIVE PRECISION:** Provide exact numbers, not ranges
2. **INSTITUTIONAL RIGOR:** Decision must withstand investment committee scrutiny  
3. **RISK-FIRST MENTALITY:** Downside protection is paramount
4. **SYSTEMATIC APPROACH:** Repeatable decision-making process
5. **PERFORMANCE ATTRIBUTION:** Clear tracking of decision factors
6. **CONTINUOUS IMPROVEMENT:** Learning from past decisions and market evolution

## 🚨 FINAL REQUIREMENTS

- **DECISION CONFIDENCE:** Must express high confidence (7+ out of 10) to recommend BUY/SELL
- **RISK JUSTIFICATION:** Every risk must have a specific mitigation strategy
- **PERFORMANCE TRACKING:** Include specific metrics for measuring success
- **EXIT STRATEGY:** Clear conditions for exiting the position
- **COMMITTEE DEFENSE:** Be prepared to defend decision to investment committee

Remember: This decision affects real money and real careers. Your recommendation will be executed with institutional capital. Make it worthy of your 25-year track record and fiduciary responsibility to investors.

CONCLUDE WITH: 'FINAL INSTITUTIONAL DECISION: **[DECISION]**' where [DECISION] is your primary recommendation.
"""

        # Create message structure for the LLM
        messages = [
            {
                "role": "system",
                "content": "You are a senior institutional portfolio manager making sophisticated investment decisions with comprehensive analysis and rigorous risk management."
            },
            {
                "role": "user", 
                "content": enterprise_trading_prompt
            }
        ]

        # Generate the decision
        result = llm.invoke(messages)

        return {
            "messages": [result],
            "enterprise_trader_decision": result.content,
            "sender": name,
            "decision_confidence": extract_decision_confidence(result.content),
            "position_size": extract_position_size(result.content),
            "risk_parameters": extract_risk_parameters(result.content)
        }

    return functools.partial(enterprise_trader_node, name="Enterprise_Trader")


def extract_decision_confidence(content: str) -> float:
    """Extract confidence level from trading decision"""
    try:
        import re
        confidence_match = re.search(r'CONVICTION LEVEL:.*?(\d+(?:\.\d+)?)', content, re.IGNORECASE)
        if confidence_match:
            return float(confidence_match.group(1)) / 10.0
        return 0.7
    except:
        return 0.7


def extract_position_size(content: str) -> dict:
    """Extract position sizing information"""
    try:
        import re
        size_match = re.search(r'Final Position Size:.*?\$([0-9,]+)', content, re.IGNORECASE)
        percent_match = re.search(r'Final Position Size:.*?\(([0-9.]+)%\)', content, re.IGNORECASE)
        
        result = {}
        if size_match:
            result['dollar_amount'] = float(size_match.group(1).replace(',', ''))
        if percent_match:
            result['portfolio_percent'] = float(percent_match.group(1))
            
        return result
    except:
        return {}


def extract_risk_parameters(content: str) -> dict:
    """Extract risk management parameters"""
    try:
        import re
        
        # Extract stop loss
        stop_match = re.search(r'Hard Stop Loss:.*?\$([0-9.]+)', content, re.IGNORECASE)
        
        # Extract max risk
        risk_match = re.search(r'Maximum Risk.*?\$([0-9,]+)', content, re.IGNORECASE)
        
        result = {}
        if stop_match:
            result['stop_loss'] = float(stop_match.group(1))
        if risk_match:
            result['max_risk'] = float(risk_match.group(1).replace(',', ''))
            
        return result
    except:
        return {}
