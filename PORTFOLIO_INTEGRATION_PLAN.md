# Portfolio Integration Plan

## Current Status
Multi-stock portfolio functionality is partially integrated into the Flask chat interface.

## Completed Steps

### 1. State Variables Added (`flask_chat_app.py:59-64`)
```python
# Portfolio mode state
portfolio_mode = False
portfolio_tickers = []  # List of tickers to analyze
current_portfolio_ticker_index = 0  # Current ticker being analyzed
portfolio_results = {}  # Store results for each stock
portfolio_trade_date = None  # Shared trade date for all stocks
```

### 2. Welcome Message Updated
Added note about multi-stock support: "You can analyze multiple stocks for portfolio optimization (e.g., 'NVDA, AAPL')"

### 3. Existing Portfolio Components Identified
- `tradingagents/portfolio/stock_data_aggregator.py` - Loads CSV results from single-stock analyses
- `tradingagents/portfolio/multi_scenario_portfolio_optimizer.py` - Runs 5 optimization algorithms
- `tradingagents/portfolio/portfolio_trader.py` - LLM makes final allocation decision
- `tradingagents/portfolio/portfolio_report_generator.py` - Creates markdown portfolio report

## Remaining Implementation Tasks

### Task 1: Modify `handle_initial_setup` to Detect Multi-Ticker Requests

**Location**: `flask_chat_app.py:~line 240`

**Changes Needed**:
1. Parse message for multiple tickers (e.g., "NVDA, AAPL" or "NVDA and AAPL")
2. If multiple tickers found:
   - Set `portfolio_mode = True`
   - Store all tickers in `portfolio_tickers`
   - Set `current_portfolio_ticker_index = 0`
   - Start analysis with first ticker
3. Display progress message: "Portfolio Mode: Analyzing 1 of 3 stocks: NVDA"

**Example Code**:
```python
# Detect multiple tickers
ticker_matches = re.findall(r'\b([A-Z]{2,5})\b', message)
if len(ticker_matches) > 1:
    # Portfolio mode
    portfolio_mode = True
    portfolio_tickers = ticker_matches
    current_portfolio_ticker_index = 0
    portfolio_trade_date = datetime.now().strftime("%Y-%m-%d")
    ticker = portfolio_tickers[0]

    # Show portfolio progress
    response_msg = f"""**PORTFOLIO MODE ACTIVATED**

Analyzing {len(portfolio_tickers)} stocks: {', '.join(portfolio_tickers)}

Starting with stock 1 of {len(portfolio_tickers)}: **{ticker}**

(Each stock will go through the full analyst workflow)
"""
else:
    # Single stock mode (existing logic)
    ticker = ticker_matches[0]
```

### Task 2: Modify Workflow to Save Portfolio Results

**Location**: After final decision is approved

**Changes Needed**:
1. When `portfolio_mode == True` and final decision is approved:
   - Save current stock's results to `portfolio_results[ticker]`
   - Increment `current_portfolio_ticker_index`
2. If more tickers remain:
   - Reset controller state for next stock
   - Start next stock analysis
3. If all stocks complete:
   - Trigger portfolio optimization

**Example Code** (add to final decision handler):
```python
if portfolio_mode:
    # Save current stock results
    current_ticker = portfolio_tickers[current_portfolio_ticker_index]
    portfolio_results[current_ticker] = {
        'state': controller.workflow_state.agent_state,
        'report': controller.workflow_state.final_report,
        'decision': controller.workflow_state.final_decision
    }

    # Check if more stocks to analyze
    if current_portfolio_ticker_index + 1 < len(portfolio_tickers):
        current_portfolio_ticker_index += 1
        next_ticker = portfolio_tickers[current_portfolio_ticker_index]

        # Reset controller for next stock
        controller.reset_workflow(next_ticker, portfolio_trade_date)

        return jsonify({
            'response': f"""✅ {current_ticker} analysis complete!

**Progress: Stock {current_portfolio_ticker_index + 1} of {len(portfolio_tickers)}**

Now analyzing: **{next_ticker}**

Proceeding with analyst workflow...
""",
            'waiting_for': 'feedback'  # Start analyst loop for next stock
        })
    else:
        # All stocks complete - trigger portfolio optimization
        return handle_portfolio_optimization()
```

### Task 3: Implement Portfolio Optimization Handler

**Location**: New function in `flask_chat_app.py`

**Purpose**: Aggregate results, run optimization, generate report

**Implementation**:
```python
def handle_portfolio_optimization():
    """Run portfolio optimization after all stocks analyzed"""
    global portfolio_mode, portfolio_tickers, portfolio_results, portfolio_trade_date

    print(f"[PORTFOLIO] All stocks complete. Running optimization...", flush=True)

    # Import portfolio components
    from tradingagents.portfolio.stock_data_aggregator import StockDataAggregator
    from tradingagents.portfolio.multi_scenario_portfolio_optimizer import MultiScenarioPortfolioOptimizer
    from tradingagents.portfolio.portfolio_report_generator import PortfolioReportGenerator
    import pandas as pd
    import yfinance as yf

    # Step 1: Aggregate stock data
    aggregator = StockDataAggregator(portfolio_trade_date)
    aggregated_result = aggregator.aggregate_multiple_stocks(portfolio_tickers)

    if aggregated_result['num_stocks'] < 2:
        return jsonify({
            'response': "⚠️ Portfolio optimization requires at least 2 stocks with complete data.",
            'waiting_for': None
        })

    # Step 2: Get returns data for optimization
    returns_data = {}
    for ticker in aggregated_result['stocks_data'].keys():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")
            if not hist.empty:
                returns_data[ticker] = hist['Close'].pct_change().dropna()
        except Exception as e:
            print(f"[PORTFOLIO] Error fetching {ticker}: {e}", flush=True)

    if len(returns_data) < 2:
        return jsonify({
            'response': "⚠️ Could not fetch price data for optimization.",
            'waiting_for': None
        })

    returns_df = pd.DataFrame(returns_data).dropna()

    # Step 3: Run optimization
    stock_metrics = {ticker: data['metrics'] for ticker, data in aggregated_result['stocks_data'].items()}
    optimizer = MultiScenarioPortfolioOptimizer(returns_df, stock_metrics)
    optimization_scenarios = optimizer.optimize_all_scenarios()

    # Step 4: Generate portfolio report
    report_generator = PortfolioReportGenerator(
        aggregated_result,
        optimization_scenarios,
        portfolio_trade_date
    )
    report_path = report_generator.generate_comprehensive_report()

    # Step 5: Extract final allocation from report
    with open(report_path, 'r', encoding='utf-8') as f:
        portfolio_report = f.read()

    # Reset portfolio mode
    portfolio_mode = False
    portfolio_results = {}

    return jsonify({
        'response': f"""✅ **PORTFOLIO ANALYSIS COMPLETE**

Analyzed {len(portfolio_tickers)} stocks: {', '.join(portfolio_tickers)}

**Multi-Scenario Optimization Results:**
- Generated {len(optimization_scenarios)} optimization scenarios
- Scenarios: Max Sharpe, Min Variance, Risk Parity, Max Diversification, HRP

**Report Location:** `{report_path}`

---

{portfolio_report[:2000]}... (full report in file)

Portfolio mode complete!
""",
        'waiting_for': None
    })
```

### Task 4: Add Required Imports

**Location**: Top of `flask_chat_app.py`

**Add**:
```python
import pandas as pd
import yfinance as yf
```

## Testing Plan

### Test 1: Single Stock (Baseline)
- Input: "Analyze NVDA"
- Expected: Normal single-stock flow (no portfolio mode)

### Test 2: Two Stock Portfolio
- Input: "Analyze NVDA and AAPL"
- Expected:
  1. Detects 2 tickers
  2. Enables portfolio mode
  3. Analyzes NVDA first (all analysts + approval)
  4. Then analyzes AAPL (all analysts + approval)
  5. Runs portfolio optimization
  6. Generates portfolio report

### Test 3: Three Stock Portfolio
- Input: "NVDA, AAPL, MSFT"
- Expected: Same as Test 2 but with 3 stocks

## Integration Complexity

**Estimated Implementation Time**: 2-3 hours

**Complexity Level**: Medium
- Requires modifying existing workflow logic
- Need to handle state transitions between stocks
- Must integrate with existing portfolio classes

## Alternative: Simpler MVP Approach

If full integration is too complex, consider a simpler approach:

1. User completes single-stock analyses separately
2. Add new endpoint `/api/portfolio/generate` that:
   - Takes list of pre-analyzed tickers
   - Loads results from `results/{TICKER}/{DATE}/csv_data/`
   - Runs portfolio optimization
   - Returns portfolio report

This decouples portfolio generation from the interactive workflow.

## Next Steps

1. Implement Task 1: Multi-ticker detection in `handle_initial_setup`
2. Implement Task 2: Portfolio result saving and sequential analysis
3. Implement Task 3: Portfolio optimization handler
4. Add Task 4: Required imports
5. Test with 2-stock portfolio (NVDA, AAPL)
6. Test with 3-stock portfolio
7. Document user workflow in README

## Files to Modify

1. `flask_chat_app.py` - Main integration point (Tasks 1-4)
2. Optionally: `static/chat.html` - Add portfolio progress indicator

## Expected User Flow

```
User: "market and fundamentals"
System: "Selected: Market/Technical, Fundamentals. Now provide stock ticker(s)..."

User: "Analyze NVDA and AAPL"
System: "PORTFOLIO MODE ACTIVATED. Analyzing 2 stocks. Starting with NVDA (1 of 2)..."

[NVDA analysis - all analysts, user approvals]

System: "✅ NVDA complete! Now analyzing AAPL (2 of 2)..."

[AAPL analysis - all analysts, user approvals]

System: "✅ All stocks complete! Running portfolio optimization...
         Generated 5 optimization scenarios...
         Final recommendation: NVDA 67.3%, AAPL 32.7%...
         Report saved to: portfolio_results/2025-10-17/portfolio_analysis_2025-10-17.md"
```

## Conclusion

The portfolio integration is well-designed and leverages existing components. The main implementation work is in coordinating the sequential stock analysis workflow and triggering optimization at the end. Once implemented, users will be able to analyze multiple stocks and receive optimized portfolio allocations in a single interactive session.
