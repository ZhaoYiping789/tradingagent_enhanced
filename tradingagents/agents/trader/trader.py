import functools
import time
import json


def create_trader(llm, memory):
    def trader_node(state, name):
        # Escape curly braces to prevent ChatPromptTemplate variable interpretation
        def escape_braces(text):
            if isinstance(text, str):
                return text.replace("{", "{{").replace("}", "}}")
            return text

        company_name = state["company_of_interest"]
        investment_plan = escape_braces(state["investment_plan"])
        market_research_report = escape_braces(state["market_report"])
        sentiment_report = escape_braces(state["sentiment_report"])
        news_report = escape_braces(state["news_report"])
        fundamentals_report = escape_braces(state["fundamentals_report"])
        quantitative_report = escape_braces(state.get("quantitative_report", "No quantitative analysis"))
        comprehensive_quant_report = escape_braces(state.get("comprehensive_quantitative_report", ""))
        optimization_results = state.get("optimization_results", {})

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}\n\n{quantitative_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        # Construct detailed analyst reports section
        detailed_reports = f"""
## 📋 DETAILED ANALYST REPORTS (MUST READ AND REFERENCE)

### Market/Technical Analysis:
{market_research_report}

### News & Sentiment Analysis:
{news_report}
{sentiment_report}

### Fundamental Analysis:
{fundamentals_report}

### Quantitative Analysis:
{quantitative_report}

### Comprehensive Quantitative Analysis:
{comprehensive_quant_report}

---

## 📊 SYNTHESIZED INVESTMENT PLAN:
{investment_plan}

---

**YOUR TASK**: Read ALL the detailed analyst reports above carefully. Your trading decision MUST explicitly reference specific details from each report (e.g., "Fundamentals show revenue grew 114% to $130B", "RSI at 64 suggests near overbought", "Optimization scenarios suggest 20-50% range"). Do NOT make generic decisions - show you've analyzed each piece of evidence.
"""

        context = {
            "role": "user",
            "content": detailed_reports,
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
                # Handle different optimization methods - only show gamma if it exists (mean-variance uses gamma, others don't)
                gamma_str = f" (γ={data['gamma']})" if 'gamma' in data else ""
                optimization_guidance += f"- **{data['philosophy']}**{gamma_str}: {data['optimal_weight']:.1%} position | {data['description']}\n"
            
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

⚠️ MANDATORY INTEGRATION PROCESS - READ ALL REPORTS:
You have received analysis from multiple specialist analysts. YOU MUST REVIEW AND INTEGRATE **ALL** AVAILABLE REPORTS:

**Required Analysts to Review:**
1. **Technical/Market Analyst**: RSI, MACD, moving averages, support/resistance, price action
2. **Fundamentals Analyst**: Financial health, revenue, margins, cash flow, P/E ratios
3. **News Analyst**: Recent news, company announcements, industry developments
4. **Sentiment/Social Analyst**: Market sentiment, social media buzz, investor mood
5. **Comprehensive Quantitative Analyst**: Statistical models, optimization scenarios, risk metrics

⚠️ CRITICAL: Check which reports are available below. If a report contains actual analysis data (not "No ... analysis available"), you MUST reference it in your decision.

YOUR INTEGRATION PROCESS:
Step 1: **Review Each Available Report** - Read and extract key insights from EVERY report that has actual data
Step 2: **Identify Convergence/Divergence** - Note where analyses agree or conflict
Step 3: **Synthesize** - Determine which optimization scenario (if available) aligns with the overall picture
Step 4: **Make Final Decision** - Your decision must explicitly reference insights from ALL available reports

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
5. **MUST specify time horizon (1-3 months, 3-12 months, or 1-3 years) - THIS IS MANDATORY**
6. Address risk management and portfolio impact
7. Present entry/exit/stop-loss/targets in clear TABLE FORMAT

Your response must include:

📊 TRADING EXECUTION PLAN:
- **Primary Recommendation:** [ACCUMULATE GRADUALLY/BUY/HOLD/REDUCE GRADUALLY/AVOID]
- **⏰ TIME HORIZON (MANDATORY):** [Specific timeframe: 1-3 months / 3-12 months / 1-3 years with detailed rationale based on analyst reports and market conditions]
- **Position Size:** [Use realistic decimals: 17.3%, 8.7%, 22.4%, NOT 15%, 10%, 20% - specify exact percentage with one decimal]
- **Confidence Level:** [1-10 scale with one decimal: 7.3/10, 8.7/10, NOT 7/10, 9/10]

💰 ENTRY & EXIT STRATEGY (TABLE FORMAT - MANDATORY):

⚠️ **CRITICAL PRICE PRECISION RULE**:
- Use REALISTIC decimal prices (e.g., $147.23, $203.67, NOT $150.00, $200.00)
- Use REALISTIC percentages with decimals (e.g., 23.7%, 47.3%, 8.2%, NOT 25%, 50%, 10%)
- Avoid overly round numbers - institutional traders use precise values based on technical levels
- Base prices on actual support/resistance levels, Fibonacci retracements, or key moving averages from technical analysis

| Strategy Component | Price Level | % of Position | Distance from Current | Rationale |
|-------------------|-------------|---------------|----------------------|-----------|
| **Primary Entry** | $XXX.XX | XX.X% | -X.X% / At Market | [Why this entry point - reference specific technical level] |
| **Secondary Entry** | $XXX.XX | XX.X% | -X.X% | [Scaling logic - reference support level] |
| **Opportunistic Entry** | $XXX.XX | XX.X% | -X.X% | [Dip-buying opportunity - reference strong support] |
| **Target Price 1 (Conservative)** | $XXX.XX | Sell XX.X% | +X.X% | [First profit target - reference resistance level] |
| **Target Price 2 (Base Case)** | $XXX.XX | Sell XX.X% | +X.X% | [Main profit target - reference key resistance] |
| **Target Price 3 (Optimistic)** | $XXX.XX | Sell XX.X% | +X.X% | [Stretch target - reference extended target] |
| **Stop Loss (Tight)** | $XXX.XX | Exit XX.X% | -X.X% | [Initial protection - below key support] |
| **Stop Loss (Wide)** | $XXX.XX | Exit 100% | -X.X% | [Portfolio protection - major support break] |

**Current Market Price:** $XXX.XX (for reference - use actual current price from data)

⚠️ RISK MANAGEMENT FRAMEWORK (TABLE FORMAT - MANDATORY):

⚠️ **PRECISION RULE**: Use realistic decimals (e.g., 13.7%, 2.3:1, 0.67) NOT round numbers (15%, 2:1, 0.5)

| Risk Parameter | Value | Impact | Management Action |
|---------------|-------|--------|-------------------|
| **Position Limit** | XX.X% | Maximum portfolio allocation | [Cap reasoning] |
| **Risk Budget** | XX.X% | Total portfolio risk | [Risk allocation logic] |
| **Max Loss Per Position** | -XX.X% | Maximum acceptable loss | [Stop-loss trigger] |
| **Risk/Reward Ratio** | X.X:1 | Profit vs loss potential | [Target/stop ratio] |
| **Volatility Adjustment** | XX.X% ATR | Position size scaling | [Vol-based sizing] |
| **Correlation Risk** | X.XX | Portfolio diversification | [Hedging needs] |

📅 DETAILED EXECUTION TIMELINE (STEP-BY-STEP - MANDATORY):

| Timeline | Action | Position Size | Price Target | Notes |
|----------|--------|---------------|--------------|-------|
| **Week 1** | Initial entry | XX% of total | $XXX.XX | [Specific action plan] |
| **Week 2** | Assessment + Scale | +XX% if conditions met | $XXX.XX or better | [Scaling conditions] |
| **Week 3-4** | Continue scaling | +XX% gradually | $XXX.XX average | [Build to target position] |
| **Month 2** | Position review | Hold XX% total | Monitor support at $XXX | [Review checkpoints] |
| **Month 3** | Profit-taking begins | Start trimming if >+XX% | Above $XXX.XX | [Profit-taking rules] |
| **Quarterly** | Strategic review | Rebalance if needed | Reassess thesis | [Long-term adjustment] |

**⏰ TOTAL TIME HORIZON FOR THIS STRATEGY:** [X months/years - be very specific about when you expect to exit]

🧠 DETAILED STRATEGY RATIONALE (REFERENCE ALL ANALYST REPORTS):

**Why This Strategy Works:**
1. **Fundamentals Support:** [Cite specific fundamental metrics from fundamentals analyst]
2. **Technical Setup:** [Reference specific technical levels from technical analyst - RSI, MACD, support/resistance]
3. **Sentiment Alignment:** [Discuss news/sentiment findings]
4. **Quantitative Validation:** [Reference optimization scenarios and which scenario this aligns with]
5. **Time Horizon Justification:** [Why this specific time period makes sense given the catalysts and market conditions]
6. **Risk-Adjusted Return:** [Expected return vs risk over the time horizon]

📊 SCENARIO ANALYSIS (WITH TIME HORIZON IMPACT):

| Scenario | Probability | Price Impact | Time to Target | Strategy Adjustment |
|----------|-------------|--------------|----------------|---------------------|
| **Bull Case (+20-30%)** | XX% | $XXX.XX in X months | X-X months | [Specific actions] |
| **Base Case (Expected)** | XX% | $XXX.XX in X months | X-X months | [Current plan execution] |
| **Bear Case (-10-20%)** | XX% | $XXX.XX in X months | Extend to X months | [Risk mitigation measures] |

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
