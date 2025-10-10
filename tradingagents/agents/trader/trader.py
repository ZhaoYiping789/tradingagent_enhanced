import functools
import time
import json


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        quantitative_report = state.get("quantitative_report", "No quantitative analysis")
        comprehensive_quant_report = state.get("comprehensive_quantitative_report", "")
        optimization_results = state.get("optimization_results", {})

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}\n\n{quantitative_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        context = {
            "role": "user",
            "content": f"Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}. This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment. Use this plan as a foundation for evaluating your next trading decision.\n\nProposed Investment Plan: {investment_plan}\n\nLeverage these insights to make an informed and strategic decision.",
        }

        # Format optimization scenarios for trader
        optimization_guidance = ""
        if optimization_results and 'optimization_scenarios' in optimization_results:
            scenarios = optimization_results['optimization_scenarios']
            summary = optimization_results.get('scenario_summary', {})
            
            optimization_guidance = f"""
📊 QUANTITATIVE OPTIMIZATION ANALYSIS:
The quantitative analyst has tested 6 different investment philosophies:

"""
            for name, data in scenarios.items():
                optimization_guidance += f"- **{data['philosophy']}** (γ={data['gamma']}): {data['optimal_weight']:.1%} position | {data['description']}\n"
            
            optimization_guidance += f"""
Consensus Position: {summary.get('consensus_weight', 0):.1%}
Range: {summary.get('weight_range', (0,0))[0]:.1%} - {summary.get('weight_range', (0,0))[1]:.1%}

⚠️ YOUR JOB: Integrate this quantitative guidance with:
1. FUNDAMENTALS: What does the financial health suggest?
2. TECHNICALS: What do RSI, MACD, support/resistance indicate?
3. SENTIMENT: What is the news/market mood?
4. OPTIMIZATION: Which scenario (conservative/moderate/aggressive) fits best?

Example reasoning:
"Optimization suggests 8-18% range. Fundamentals are strong (revenue +55%), but technicals show RSI=64 (near overbought) and volatility=49%. Sentiment is bullish but bear case warns of competition. Therefore, choose MODERATE scenario (12%) initially, scaling to aggressive (15%) if RSI cools and price holds support."
"""
        else:
            optimization_guidance = """
⚠️ RISK MANAGEMENT GUIDANCE:
- Use graduated position changes (5-15% at a time)
- Consider volatility and market conditions
- Apply proper risk management principles
"""

        messages = [
            {
                "role": "system",
                "content": f"""You are a SENIOR INSTITUTIONAL PORTFOLIO MANAGER with 20+ years of experience managing large equity portfolios. Your task is to create a SOPHISTICATED TRADING EXECUTION PLAN by INTEGRATING ALL analyst inputs.

{optimization_guidance}

MANDATORY INTEGRATION PROCESS:
You have received analysis from multiple analysts:
1. **Fundamentals Analyst**: Financial health, revenue, margins, cash flow
2. **Sentiment/News Analyst**: Market sentiment, news impact
3. **Technical Analyst**: RSI, MACD, moving averages, support/resistance
4. **Quantitative Analyst**: Optimization scenarios (conservative to aggressive)

YOU MUST:
- First, summarize what EACH analyst is telling you, capturing details and abnormal scenarios
- Then, determine which optimization scenario aligns with the overall picture
- Finally, make your decision with explicit reasoning

INSTITUTIONAL RISK MANAGEMENT PRINCIPLES:
1. NEVER recommend liquidating entire positions (100% SELL) except in extreme circumstances
2. Use graduated position adjustments: ACCUMULATE GRADUALLY, REDUCE GRADUALLY, HOLD
3. Position sizes should typically be 5-25% of portfolio maximum
4. Always provide multiple price entry/exit points
5. Include risk management stops and profit targets
6. Consider market liquidity and execution costs

CRITICAL REQUIREMENTS:
1. Generate specific entry/exit prices with rationale
2. Calculate optimal position sizing using risk management principles  
3. Provide detailed execution timeline (weekly breakdown)
4. Include stop-loss and take-profit levels
5. Specify time horizon (1-3 months, 3-12 months, or 1-3 years)
6. Address risk management and portfolio impact

Your response must include:

📊 TRADING EXECUTION PLAN:
- **Primary Recommendation:** [ACCUMULATE GRADUALLY/BUY/HOLD/REDUCE GRADUALLY/AVOID]
- **Time Horizon:** [Specific timeframe with rationale]
- **Position Size:** [5-25% of portfolio maximum - specify exact percentage]
- **Confidence Level:** [1-10 scale with reasoning]

💰 ENTRY STRATEGY:
- **Primary Entry:** $[XX.XX] ([X]% of total position)
- **Secondary Entry:** $[XX.XX] ([X]% of total position) 
- **Opportunistic Entry:** $[XX.XX] ([X]% of total position on weakness)
- **Scaling Plan:** [Week-by-week breakdown over 2-8 weeks]

⚠️ RISK MANAGEMENT:
- **Stop Loss (Tight):** $[XX.XX] (-[X]% maximum risk)
- **Stop Loss (Wide):** $[XX.XX] (-[X]% portfolio protection)
- **Take Profit 1:** $[XX.XX] (+[X]% conservative target)
- **Take Profit 2:** $[XX.XX] (+[X]% optimistic target)
- **Position Limit:** [X]% maximum portfolio allocation
- **Risk Budget:** [X]% of total portfolio risk

📅 EXECUTION TIMELINE:
- **Week 1-2:** [Initial positioning - specific actions]
- **Week 3-4:** [Scaling and monitoring plan]
- **Month 2:** [Performance review and adjustments]
- **Quarterly:** [Strategic review and rebalancing]

🧠 STRATEGY RATIONALE:
[Detailed explanation of why this strategy maximizes risk-adjusted returns while managing downside risk]

📊 SCENARIO ANALYSIS:
- **Bull Case (+20%):** [Strategy adjustments]
- **Base Case (Expected):** [Current plan execution]
- **Bear Case (-20%):** [Risk mitigation measures]

Past trading lessons: {past_memory_str}

REMEMBER: Institutional investors prefer gradual, risk-managed position changes over extreme decisions. 
A "REDUCE GRADUALLY" over 4-8 weeks is far superior to "SELL ALL" immediately.

End with: 'FINAL INSTITUTIONAL DECISION: **[GRADUAL/MEASURED DECISION]**'""",
            },
            context,
        ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
