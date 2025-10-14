# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradingAgents Enhanced Edition is an AI-powered institutional-grade trading analysis system that uses multi-agent collaboration (via LangGraph) to analyze stocks and generate comprehensive investment reports. It supports both single-stock and multi-stock portfolio analysis with advanced quantitative optimization.

**Key Innovation**: This system simulates an institutional investment committee using specialized AI agents (market analysts, fundamental analysts, news analysts, etc.) that debate and collaborate to produce professional-grade trading decisions and reports.

## Development Commands

### Environment Setup
```bash
# Install dependencies (recommended - uses UV package manager)
uv sync

# Alternative: Standard pip install
pip install -r requirements.txt

# Set required environment variables
export OPENAI_API_KEY="your-api-key-here"
```

### Running Analyses

**Single Stock Analysis:**
```bash
# Full enterprise analysis (main entry point - OpenAI)
uv run main_enterprise.py

# Full enterprise analysis (WatsonX)
uv run main_enterprise_watsonx.py

# Lightweight analysis (faster, fewer agents)
uv run single_stock_analysis.py
```

**Portfolio Analysis (Multiple Stocks):**
```bash
# Edit main_enterprise.py first:
# Set portfolio_mode = True
# Set portfolio_tickers = ["NVDA", "AAPL", "MSFT"]

uv run main_enterprise.py

# Standalone portfolio analysis (requires existing single stock results)
uv run run_portfolio_analysis.py
```

### Output Locations

- **Single Stock Results**: `results/{TICKER}/{DATE}/`
  - Markdown report: `{TICKER}_comprehensive_analysis_{DATE}.md`
  - Word document: `{TICKER}_comprehensive_analysis_{DATE}.docx`
  - Charts: `{TICKER}_comprehensive_analysis_{DATE}.png`
  - CSV data: `csv_data/` subdirectory (6 files)

- **Portfolio Results**: `portfolio_results/{DATE}/portfolio_analysis_{DATE}.md`

- **Debug Logs**: `eval_results/{TICKER}/TradingAgentsStrategy_logs/`

- **Runtime Logs**: `enterprise_output.log`, `analysis_output.log`

## Architecture Overview

### Multi-Agent System Architecture

The system uses **LangGraph** to orchestrate a workflow of specialized AI agents that collaborate like an institutional investment team:

**Core Agent Types** (in `tradingagents/agents/`):

1. **Analysts** (`analysts/`):
   - `market_analyst.py` - Technical analysis (RSI, MACD, Bollinger Bands)
   - `fundamentals_analyst.py` - Financial metrics (P/E, revenue, cash flow)
   - `news_analyst.py` - News sentiment and impact
   - `social_media_analyst.py` - Reddit/Twitter sentiment
   - `comprehensive_quantitative_analyst.py` - ML forecasting (GARCH, statistical models)
   - `portfolio_analyst.py` - Cross-stock correlation and diversification
   - `enterprise_strategy_analyst.py` - Strategic institutional analysis

2. **Investment Committee Simulation** (`researchers/`, `managers/`):
   - `bull_researcher.py` / `bear_researcher.py` - Debate pros/cons
   - `research_manager.py` - Moderates investment debate

3. **Risk Committee** (`risk_mgmt/`):
   - `conservative_debator.py` / `neutral_debator.py` / `aggressive_debator.py`
   - `risk_manager.py` - Moderates risk assessment

4. **Decision Makers** (`trader/`):
   - `trader.py` - Standard trading decisions
   - `enterprise_trader.py` - Institutional trading plans with position sizing

5. **Report Generators** (`generators/`):
   - `enhanced_quantitative_document_generator.py` - Creates Word/Markdown reports
   - `comprehensive_charts.py` - Multi-panel technical chart generation

### LangGraph Workflow System

The workflow is defined in `tradingagents/graph/`:

- `trading_graph.py` - Main orchestrator class (`TradingAgentsGraph`)
- `setup.py` - Graph construction, node definitions
- `propagation.py` - State propagation through the graph
- `conditional_logic.py` - Routing logic between agents
- `signal_processing.py` - Processes agent outputs

**State Management**: `agents/utils/agent_states.py` defines:
- `AgentState` - Main analysis state (extends LangGraph's `MessagesState`)
- `InvestDebateState` - Investment committee debate state
- `RiskDebateState` - Risk committee debate state

### Portfolio Optimization System

Located in `tradingagents/portfolio/`:

- `stock_data_aggregator.py` - Loads and combines multiple stock analyses
- `multi_scenario_portfolio_optimizer.py` - Runs 5+ optimization algorithms:
  - Kelly Criterion
  - Mean-Variance Optimization
  - Risk Parity
  - Minimum Variance
  - Maximum Sharpe Ratio
  - VaR/CVaR constraints
- `portfolio_trader.py` - LLM-powered final allocation decision
- `portfolio_report_generator.py` - Creates comprehensive portfolio reports
- `csv_data_exporter.py` - Exports structured data

### Data Flow System

`tradingagents/dataflows/` handles external data:

- `interface.py` - Main data interface
- `yfin_utils.py` - Yahoo Finance integration
- `finnhub_utils.py` - Finnhub API
- `googlenews_utils.py` - News scraping
- `reddit_utils.py` - Reddit sentiment
- `stockstats_utils.py` - Technical indicators

## Configuration System

### Main Configuration

`tradingagents/default_config.py` defines `DEFAULT_CONFIG` with:
- LLM provider settings (`llm_provider`, `deep_think_llm`, `quick_think_llm`)
- API endpoints (`backend_url`)
- Debate parameters (`max_debate_rounds`, `max_risk_discuss_rounds`)
- Tool settings (`online_tools`)

### Customizing Analysis

In `main_enterprise.py`, modify:

```python
# Analysis scope
portfolio_mode = False  # True for portfolio, False for single stock
portfolio_tickers = ["NVDA", "AAPL", "MSFT"]
company_of_interest = "NVDA"  # For single stock mode
current_date = "2025-10-09"

# Agent selection
selected_analysts = [
    "market",          # Technical analysis
    "fundamentals",    # Financial analysis
    "news",            # News sentiment
    "social",          # Social media sentiment
    "comprehensive_quantitative",  # ML forecasting
    "portfolio",       # Portfolio impact
    "enterprise_strategy"  # Strategic analysis
]

# LLM configuration
config = {
    "llm_provider": "openai",  # or "anthropic", "google", "watsonx"
    "deep_think_llm": "gpt-4o",      # Complex reasoning
    "quick_think_llm": "gpt-4o-mini", # Fast operations
    "max_debate_rounds": 2,           # Investment debate depth
    "enterprise_mode": True,          # Enable enterprise features
    "lightweight_quantitative": False, # Full optimization algorithms
}
```

## LLM Provider Support

The system supports multiple LLM providers (configured via `llm_provider` in config):

- **OpenAI** (default): GPT-4, GPT-4-turbo, GPT-3.5
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Haiku
- **Google**: Gemini 1.5 Pro, Gemini 1.5 Flash
- **WatsonX** (✅ production ready): IBM WatsonX.ai models

### WatsonX Integration

**Entry Point**: `main_enterprise_watsonx.py`

**Recommended Models**:
- `mistralai/mixtral-8x7b-instruct-v01` (best tool calling support)
- `meta-llama/llama-3-3-70b-instruct` (Granite 3.0 - high quality)
- `ibm/granite-3-8b-instruct` (lightweight)

**Configuration**:
```python
config["llm_provider"] = "watsonx"
config["watsonx_url"] = "https://us-south.ml.cloud.ibm.com"
config["watsonx_project_id"] = "your-project-id"
config["watsonx_api_key"] = "your-api-key"
config["deep_think_llm"] = "mistralai/mixtral-8x7b-instruct-v01"
```

**Setup**: See `README_WATSONX.md`, `QUICK_START_WATSONX.md`, or `WATSONX_SETUP.md`

**Test**: Run `test_watsonx_connection.py` or `RUN_WATSONX_TEST.bat`

LLM initialization is in `tradingagents/graph/trading_graph.py:60-112`.

## Key Implementation Patterns

### Adding a New Analyst

1. Create analyst in `tradingagents/agents/analysts/my_analyst.py`
2. Define a `create_my_analyst(llm, toolkit)` function
3. Add node creation in `tradingagents/graph/setup.py:64-120`
4. Add report field to `AgentState` in `agents/utils/agent_states.py`
5. Add routing logic in `graph/conditional_logic.py` if needed

### State Management

All agents operate on shared state (`AgentState`). Agents receive state, perform analysis, and return updated state with their findings. Key state fields:

- `company_of_interest`, `trade_date` - Analysis targets
- `{analyst}_report` - Individual analyst findings
- `investment_debate_state` - Bull/bear debate results
- `risk_debate_state` - Risk committee results
- `final_trade_decision` - Ultimate recommendation

### Memory System

Agents use `FinancialSituationMemory` (in `agents/utils/memory.py`) to maintain conversation context across multiple interactions within the same session.

### Report Generation

The document generator (`enhanced_quantitative_document_generator.py`) combines all agent outputs into:
- Professional markdown report
- Word document with embedded charts
- Multi-panel technical analysis charts
- 6 CSV files with structured metrics

## Important Notes

- **API Key Required**: OpenAI (or other LLM provider) API key must be set
- **Windows Encoding**: `main_enterprise.py:26-30` handles Windows console UTF-8 encoding
- **Data Sources**: Set `online_tools: True` for real-time data, `False` for cached data
- **Analysis Date**: Use actual past dates (e.g., "2025-10-09") for realistic historical analysis
- **Portfolio Requirements**: Portfolio analysis requires existing single-stock CSV results
- **Python Version**: Requires Python 3.10+ (specified in `pyproject.toml`)

## Development Status

- ✅ **Production Ready**: Single stock analysis, portfolio optimization
- 🚧 **In Development**: IBM WatsonX integration, enhanced portfolio reporting
- 📋 **Planned**: Backtesting engine, web UI, API interface

## Troubleshooting

**If analysis fails:**
1. Check API key is set: `echo $OPENAI_API_KEY`
2. Review logs in `enterprise_output.log`
3. Check agent-specific logs in `eval_results/{TICKER}/TradingAgentsStrategy_logs/`
4. Verify dependencies: `uv sync --reinstall`

**For portfolio errors:**
1. Ensure single-stock analyses exist in `results/{TICKER}/{DATE}/csv_data/`
2. Verify at least 2 stocks have completed analyses
3. Check `portfolio_tickers` matches available data

**Memory issues:**
- Reduce number of analysts in `selected_analysts`
- Use `lightweight_quantitative: True`
- Reduce `max_debate_rounds` to 1
