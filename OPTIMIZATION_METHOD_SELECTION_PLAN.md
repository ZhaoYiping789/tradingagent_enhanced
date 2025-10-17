# 优化方法交互式选择实现计划

## 目标
在运行 comprehensive_quantitative analyst 之前，询问用户偏好，然后使用 LLM 分析偏好并选择最合适的优化方法，每个方法都提供多场景/调参结果。

## 工作流程

### 1. 用户交互流程
```
用户选择 analysts (包含 comprehensive_quantitative)
  ↓
系统询问：您的投资偏好是什么？
  - 风险偏好（保守/平衡/激进）
  - 投资目标（资本增值/收入/资本保值）
  - 约束条件（流动性需求、时间范围等）
  ↓
LLM 分析偏好
  ↓
LLM 选择最合适的优化方法（Mean-Variance / Risk Parity / Max Sharpe 等）
  ↓
运行选择的方法，生成多种调参场景的报告
```

## 实现步骤

### 步骤 1: 添加优化方法（comprehensive_quantitative_analyst.py）

添加以下优化方法：
1. **Mean-Variance Optimization** (已有)
   - 多场景：Conservative, Moderate, Aggressive, Vol-focused, Return-focused, Sharpe-optimized

2. **Risk Parity** (新增)
   - 多场景：Equal Risk Contribution, Vol-weighted, Sharpe-weighted, CVaR-weighted

3. **Minimum Variance** (新增)
   - 多场景：纯最小方差, CVaR约束, Turnover约束, Sector约束

4. **Maximum Sharpe Ratio** (新增)
   - 多场景：无约束, Long-only, 上下限约束, Tracking error约束

5. **Equal Weight Benchmark** (新增)
   - 多场景：纯等权, 波动率调整, 风险预算调整

### 步骤 2: 添加偏好询问（flask_chat_app.py）

在 `handle_initial_setup()` 中：
- 检测 selected_analysts 是否包含 'comprehensive_quantitative'
- 如果包含，询问优化偏好
- 设置 waiting_for = 'optimization_preference'

添加 `handle_optimization_preference()` 函数：
- 接收用户偏好描述
- 使用 LLM 分析偏好并选择方法
- 存储到 controller.workflow_state.agent_state['optimization_method_choice']
- 继续运行第一个 analyst

### 步骤 3: 修改 analyst 读取偏好（comprehensive_quantitative_analyst.py）

在 `comprehensive_quantitative_node()` 中：
- 从 state 读取 optimization_method_choice
- 如果没有，使用默认方法（Mean-Variance）
- 根据选择的方法，调用相应的优化函数
- 生成多场景报告

### 步骤 4: 修改报告生成函数

修改 `generate_comprehensive_quantitative_report()` 接受方法类型参数，根据不同方法生成相应的多场景报告格式。

## 数据结构

### optimization_method_choice 格式
```python
{
    'user_preference_text': "我希望稳健增长...",
    'parsed_preferences': {
        'risk_tolerance': 'moderate',
        'investment_goal': 'growth',
        'constraints': ['liquidity', 'time_horizon_medium']
    },
    'selected_method': 'risk_parity',  # mean_variance, risk_parity, min_variance, max_sharpe, equal_weight
    'method_rationale': "Based on your preference for balanced risk...",
    'scenarios_to_run': ['equal_risk', 'vol_weighted', 'sharpe_weighted', 'cvar_weighted']
}
```

## 实现代码框架

### 1. Flask App 修改（flask_chat_app.py）

```python
def handle_initial_setup(message):
    # ... existing code ...

    # Check if comprehensive_quantitative is selected
    if 'comprehensive_quantitative' in selected_analysts:
        # Ask for optimization preferences
        waiting_for = 'optimization_preference'
        return jsonify({
            'response': f"""**Stock: {ticker}**

Before running the Comprehensive Quantitative Analysis, please tell me your investment preferences:

📊 **Risk Tolerance**: Conservative / Balanced / Aggressive?
🎯 **Investment Goal**: Capital preservation / Steady growth / Maximum returns?
⏱️ **Time Horizon**: Short-term (< 1 year) / Medium-term (1-3 years) / Long-term (> 3 years)?
💰 **Special Constraints**: Any specific requirements (liquidity, sector limits, etc.)?

Example: "I prefer balanced risk with steady growth over 2-3 years, no specific constraints"
""",
            'waiting_for': 'optimization_preference',
            'ticker': ticker,
            'selected_analysts': selected_analysts
        })

    # Otherwise continue normally...
```

### 2. 添加偏好处理函数（flask_chat_app.py）

```python
def handle_optimization_preference(message, ticker, selected_analysts):
    """Use LLM to analyze preferences and select optimization method"""

    llm = WATSONX_LLM  # or controller.graph.quick_thinking_llm

    prompt = f"""Analyze the following investment preferences and select the most suitable portfolio optimization method:

User Preferences: {message}

Available Methods:
1. **mean_variance**: Markowitz Mean-Variance Optimization - balances return vs risk
2. **risk_parity**: Risk Parity - equalizes risk contribution across assets
3. **min_variance**: Minimum Variance - minimizes portfolio volatility
4. **max_sharpe**: Maximum Sharpe Ratio - optimizes risk-adjusted returns
5. **equal_weight**: Equal Weight - simple diversification benchmark

Return JSON:
{{
    "selected_method": "method_name",
    "rationale": "explanation",
    "risk_tolerance": "conservative/moderate/aggressive",
    "scenarios": ["scenario1", "scenario2", ...]
}}
"""

    response = llm.invoke(prompt)
    # Parse LLM response...

    # Store in workflow state
    controller.workflow_state.agent_state['optimization_method_choice'] = choice_data

    # Continue with analyst execution...
```

### 3. Analyst 修改（comprehensive_quantitative_analyst.py）

```python
def comprehensive_quantitative_node(state):
    # Read optimization method choice
    method_choice = state.get('optimization_method_choice', None)

    if method_choice:
        selected_method = method_choice['selected_method']
        scenarios = method_choice.get('scenarios', [])
    else:
        # Default
        selected_method = 'mean_variance'
        scenarios = ['conservative', 'moderate', 'aggressive']

    # Run selected method
    if selected_method == 'mean_variance':
        results = run_mean_variance_optimization(price_data, ticker, scenarios)
    elif selected_method == 'risk_parity':
        results = run_risk_parity_optimization(price_data, ticker, scenarios)
    # ... etc

    # Generate report with method-specific formatting
    report = generate_method_specific_report(ticker, results, selected_method, method_choice)

    return {...}
```

## 预期效果

用户体验：
1. 选择 comprehensive_quantitative analyst
2. 系统询问投资偏好
3. 用户输入："我希望在中期内获得稳定收益，风险偏好适中"
4. LLM 分析：选择 Risk Parity 方法
5. 生成报告包含：
   - Equal Risk Contribution scenario
   - Volatility-weighted scenario
   - Sharpe-weighted scenario
   - CVaR-weighted scenario
   - 每个场景的权重建议和风险指标
   - 方法选择的解释
