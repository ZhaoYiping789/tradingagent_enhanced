# TradingAgents Enterprise Edition

## 🏛️ Multi-Agent Trading Analysis System

TradingAgents is a sophisticated trading analysis system that uses multiple AI agents to analyze stocks and generate portfolio recommendations. The system combines technical analysis, fundamental analysis, sentiment analysis, and advanced portfolio optimization.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API Key
- UV package manager (recommended)

### Getting started
```bash

# Install dependencies
uv sync

# Set up environment variables
export OPENAI_API_KEY="your-api-key-here"
```

### Running the System

#### Option 1: Single Stock Analysis
```bash
# Run analysis for a single stock (default: NVDA)
uv run main_enterprise.py
```

#### Option 2: Portfolio Analysis (Multiple Stocks)
```bash
# Edit main_enterprise.py and set:
# portfolio_mode = True
# portfolio_tickers = ["NVDA", "AAPL", "MSFT"]  # Add your stocks

# Then run:
uv run main_enterprise.py
```

#### Option 3: Lightweight Single Stock Analysis
```bash
# Quick analysis without full enterprise features
uv run single_stock_analysis.py
```

#### Option 4: Standalone Portfolio Analysis
```bash
# Run portfolio analysis on existing single stock results
uv run run_portfolio_analysis.py
```

## 📁 Project Structure

```
TradingAgents-main/
├── main_enterprise.py              # Main entry point for enterprise analysis
├── single_stock_analysis.py        # Lightweight single stock analysis
├── run_portfolio_analysis.py       # Standalone portfolio analysis
├── pyproject.toml                  # Project dependencies and configuration
├── README.md                       # This file
│
├── tradingagents/                  # Core system package
│   ├── __init__.py
│   ├── default_config.py          # Default configuration settings
│   │
│   ├── agents/                    # AI agents and components
│   │   ├── __init__.py
│   │   ├── utils/                 # Shared utilities
│   │   │   ├── agent_states.py    # State management
│   │   │   ├── agent_utils.py     # Common utilities
│   │   │   └── memory.py          # Memory systems
│   │   │
│   │   ├── analysts/              # Analysis agents
│   │   │   ├── market_analyst.py           # Technical analysis
│   │   │   ├── fundamentals_analyst.py     # Financial analysis
│   │   │   ├── news_analyst.py             # News sentiment
│   │   │   ├── social_media_analyst.py     # Social sentiment
│   │   │   ├── comprehensive_quantitative_analyst.py  # ML forecasting
│   │   │   ├── multi_scenario_optimizer.py # Optimization scenarios
│   │   │   ├── portfolio_analyst.py        # Portfolio comparison
│   │   │   └── enterprise_strategy_analyst.py  # Strategic analysis
│   │   │
│   │   ├── generators/            # Report generators
│   │   │   ├── enhanced_quantitative_document_generator.py  # Main report generator
│   │   │   └── comprehensive_charts.py     # Chart generation
│   │   │
│   │   ├── traders/               # Trading decision agents
│   │   │   └── trader.py          # Main trading agent
│   │   │
│   │   ├── researchers/           # Research agents
│   │   │   ├── bull_researcher.py
│   │   │   └── bear_researcher.py
│   │   │
│   │   ├── managers/              # Management agents
│   │   │   ├── research_manager.py
│   │   │   └── risk_manager.py
│   │   │
│   │   └── risk_mgmt/             # Risk management agents
│   │       ├── aggresive_debator.py
│   │       ├── conservative_debator.py
│   │       └── neutral_debator.py
│   │
│   ├── graph/                     # LangGraph workflow system
│   │   ├── __init__.py
│   │   ├── trading_graph.py       # Main workflow graph
│   │   ├── setup.py               # Graph configuration
│   │   └── conditional_logic.py   # Workflow logic
│   │
│   ├── portfolio/                 # Portfolio optimization system
│   │   ├── stock_data_aggregator.py        # Data aggregation
│   │   ├── multi_scenario_portfolio_optimizer.py  # Optimization algorithms
│   │   ├── portfolio_report_generator.py   # Portfolio reports
│   │   ├── portfolio_trader.py             # LLM portfolio decisions
│   │   └── csv_data_exporter.py            # Data export
│   │
│   ├── optimization/              # Optimization algorithms
│   │   └── optimized_single_stock.py       # Single stock optimization
│   │
│   └── models/                    # ML models
│       └── time_series_models.py  # Time series forecasting
│
├── results/                       # Analysis results
│   └── {TICKER}/                  # Per-stock results
│       └── {DATE}/                # Per-date results
│           ├── {TICKER}_comprehensive_analysis_{DATE}.md
│           ├── {TICKER}_comprehensive_analysis_{DATE}.docx
│           ├── {TICKER}_comprehensive_analysis_{DATE}.png
│           └── csv_data/          # Exported CSV data
│               ├── summary_metrics.csv
│               ├── risk_metrics.csv
│               ├── technical_indicators.csv
│               ├── financial_metrics.csv
│               ├── optimization_scenarios.csv
│               └── sentiment_analysis.csv
│
├── portfolio_results/             # Portfolio analysis results
│   └── {DATE}/
│       └── portfolio_analysis_{DATE}.md
│
└── eval_results/                  # Evaluation and logs
    └── {TICKER}/
        └── TradingAgentsStrategy_logs/
```

## ⚙️ Configuration

### Main Configuration (main_enterprise.py)
```python
# Analysis mode
portfolio_mode = False  # Set to True for portfolio analysis
portfolio_tickers = ["NVDA", "AAPL"]  # Stocks to analyze

# Selected analysts
selected_analysts = [
    "market",           # Technical analysis
    "fundamentals",     # Financial analysis  
    "news",            # News sentiment
    "social",          # Social sentiment
    "comprehensive_quantitative",  # ML forecasting
    "portfolio"        # Portfolio comparison
]

# Current date (update as needed)
current_date = "2025-10-09"
```

### Environment Variables
```bash
# Required
export OPENAI_API_KEY="your-openai-api-key"

# Optional
export NEWS_API_KEY="your-news-api-key"
export SOCIAL_API_KEY="your-social-api-key"
```

## 📊 Output Files

### Single Stock Analysis Output
- **Markdown Report**: `{TICKER}_comprehensive_analysis_{DATE}.md`
- **Word Document**: `{TICKER}_comprehensive_analysis_{DATE}.docx`
- **Charts**: `{TICKER}_comprehensive_analysis_{DATE}.png`
- **CSV Data**: 6 CSV files with structured data

### Portfolio Analysis Output
- **Portfolio Report**: `portfolio_analysis_{DATE}.md`
- **Individual Stock Data**: Aggregated from single stock analyses

## 🔧 Troubleshooting

### Common Issues

1. **API Key Error**
   ```bash
   # Make sure your OpenAI API key is set
   export OPENAI_API_KEY="your-key-here"
   ```

2. **Dependency Issues**
   ```bash
   # Reinstall dependencies
   uv sync --reinstall
   ```

3. **Portfolio Analysis Fails**
   ```bash
   # Make sure single stock analyses are completed first
   # Check that CSV files exist in results/{TICKER}/{DATE}/csv_data/
   ```

4. **Memory Issues**
   ```bash
   # Reduce the number of analysts or stocks being analyzed
   # Edit main_enterprise.py to use fewer analysts
   ```

### Log Files
- Check `enterprise_output.log` for detailed execution logs
- Check `eval_results/{TICKER}/TradingAgentsStrategy_logs/` for agent-specific logs

## 🎯 Usage Examples

### Example 1: Analyze NVDA
```bash
# Edit main_enterprise.py
company_of_interest = "NVDA"
portfolio_mode = False

# Run analysis
uv run main_enterprise.py
```

### Example 2: Portfolio Analysis of Tech Stocks
```bash
# Edit main_enterprise.py
portfolio_mode = True
portfolio_tickers = ["NVDA", "AAPL", "MSFT", "GOOGL"]

# Run analysis
uv run main_enterprise.py
```

### Example 3: Quick Single Stock Analysis
```bash
# No configuration needed
uv run single_stock_analysis.py
```

## 📈 Understanding the Results

### Single Stock Analysis
1. **Technical Analysis**: Market trends, indicators, signals
2. **Fundamental Analysis**: Financial health, growth metrics
3. **Sentiment Analysis**: News and social media sentiment
4. **Quantitative Analysis**: ML forecasts and optimization scenarios
5. **Final Recommendation**: BUY/SELL/HOLD with confidence level

### Portfolio Analysis
1. **Individual Stock Results**: Aggregated from single stock analyses
2. **Optimization Algorithms**: 5 different allocation strategies
3. **LLM Integration**: AI-powered final allocation decision
4. **Comparative Analysis**: Side-by-side stock comparison
5. **Risk Assessment**: Portfolio-level risk metrics

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review log files for error details
3. Ensure all dependencies are properly installed
4. Verify API keys are correctly set

---

**TradingAgents Enterprise Edition** - Professional trading analysis powered by AI agents and advanced quantitative methods.