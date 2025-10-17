# TradingAgents Enhanced Edition

**AI-Powered Institutional-Grade Trading Analysis System**

Multi-agent collaborative investment analysis system based on [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents.git), supporting single-stock analysis and portfolio optimization.

---

## 🌟 Choose Your Version

This project provides **three professional versions** for different use cases. Please select the branch that best fits your needs:

### 📊 **Branch Overview**

| Branch | Use Case | Key Features | LLM Support | Recommended For |
|--------|----------|--------------|-------------|-----------------|
| **[main](https://github.com/ZhaoYiping789/tradingagent_enhanced)** | Standard CLI Analysis | OpenAI GPT-4, Complete Reports | OpenAI GPT-4 | CLI Users, Developers |
| **[watsonx-integration](https://github.com/ZhaoYiping789/tradingagent_enhanced/tree/watsonx-integration)** | IBM WatsonX Integration | IBM WatsonX.ai LLM Support | WatsonX + OpenAI | Enterprise, WatsonX Users |
| **[UI-version](https://github.com/ZhaoYiping789/tradingagent_enhanced/tree/UI-version)** | Interactive Web Interface | Web UI, Real-time Chat Analysis | WatsonX + OpenAI | All Users, Non-technical |

---

## 🚀 Quick Start Guide

### 1️⃣ Main Branch - Standard Command Line Version

**Best For**: Users familiar with command line, need standardized analysis reports

#### Installation

```bash
# Clone repository - Main branch
git clone https://github.com/ZhaoYiping789/tradingagent_enhanced.git
cd tradingagent_enhanced

# Install dependencies
uv sync

# Set OpenAI API Key
export OPENAI_API_KEY="your-openai-api-key"
```

#### Run Analysis

**Single Stock Analysis**:
```bash
# Edit main_enterprise.py to set stock ticker
# company_of_interest = "NVDA"
# portfolio_mode = False

uv run main_enterprise.py
```

**Portfolio Analysis**:
```bash
# Edit main_enterprise.py to set portfolio
# portfolio_mode = True
# portfolio_tickers = ["NVDA", "AAPL", "MSFT"]

uv run main_enterprise.py
```

**Output Location**:
- Single Stock Reports: `results/{TICKER}/{DATE}/`
  - Markdown Report: `{TICKER}_comprehensive_analysis_{DATE}.md`
  - Word Document: `{TICKER}_comprehensive_analysis_{DATE}.docx`
  - Charts: `{TICKER}_comprehensive_analysis_{DATE}.png`
  - CSV Data: `csv_data/` directory (6 files)

- Portfolio Reports: `portfolio_results/{DATE}/portfolio_analysis_{DATE}.md`

---

### 2️⃣ WatsonX Branch - IBM WatsonX.ai Integration

**Best For**: IBM WatsonX users, enterprise-grade AI analysis needs

#### Installation

```bash
# Clone WatsonX branch
git clone -b watsonx-integration https://github.com/ZhaoYiping789/tradingagent_enhanced.git
cd tradingagent_enhanced

# Install dependencies
uv sync

# Set WatsonX environment variables
export WATSONX_URL="https://us-south.ml.cloud.ibm.com"
export WATSONX_APIKEY="your-watsonx-api-key"
export WATSONX_PROJECT_ID="your-project-id"
```

#### Run Analysis

**WatsonX Single Stock Analysis**:
```bash
uv run main_enterprise_watsonx.py
```

**Test WatsonX Connection**:
```bash
# Windows
RUN_WATSONX_TEST.bat

# Linux/Mac
python test_watsonx_connection.py
```

#### Recommended Model Configuration

In `main_enterprise_watsonx.py`:

```python
config = {
    "llm_provider": "watsonx",
    "watsonx_url": "https://us-south.ml.cloud.ibm.com",
    "watsonx_project_id": "your-project-id",

    # Recommended model combination
    "deep_think_llm": "mistralai/mixtral-8x7b-instruct-v01",  # Complex analysis
    "quick_think_llm": "ibm/granite-3-8b-instruct",           # Fast operations

    # Other available models:
    # "meta-llama/llama-3-3-70b-instruct"  # Granite 3.0 - High quality
    # "ibm/granite-3-8b-instruct"          # Lightweight
}
```

**Detailed Documentation**:
- `README_WATSONX.md` - Complete WatsonX integration guide
- `QUICK_START_WATSONX.md` - WatsonX quick start
- `WATSONX_SETUP.md` - WatsonX environment setup

---

### 3️⃣ UI-version Branch - Interactive Web Interface ⭐ **Recommended for New Users**

**Best For**: All users, especially non-technical investors

#### Installation

```bash
# Clone UI version branch
git clone -b UI-version https://github.com/ZhaoYiping789/tradingagent_enhanced.git
cd tradingagent_enhanced

# Install dependencies (includes Flask, Gradio web frameworks)
uv sync

# Set environment variables (supports OpenAI or WatsonX)
export OPENAI_API_KEY="your-openai-api-key"
# OR use WatsonX:
export WATSONX_APIKEY="your-watsonx-api-key"
export WATSONX_PROJECT_ID="your-project-id"
```

#### Launch Web UI

**Option 1: Flask Chat Interface** (Recommended)
```bash
# Windows
LAUNCH_UI.bat

# Linux/Mac
python flask_chat_app.py
```

Then open in browser: `http://localhost:5000`

**Option 2: Gradio Interface**
```bash
# Windows
RUN_INTERACTIVE_UI.bat

# Linux/Mac
python -m tradingagents.interactive.gradio_ui
```

**Option 3: Simple Chat Interface**
```bash
# Windows
START_UI_SIMPLE.bat

# Linux/Mac
python -m tradingagents.interactive.simple_chat_ui
```

#### Web UI Features

✨ **Interactive Conversational Analysis**:
- 💬 Perform stock analysis through natural language conversations
- 📊 Real-time report and chart generation
- 🔄 Iterative refinement based on user feedback
- 📈 Automatic visualization chart generation

✨ **User-Friendly Interface**:
- 🖥️ Modern web interface, no command line required
- 📱 Mobile device support
- 🎨 Visual analysis dashboards
- 💾 History saving

✨ **Smart Interactions**:
- 🤖 AI assistant automatically parses user intent
- 🎯 Automatically selects appropriate analyst team
- 📝 Natural language input: e.g., "Analyze NVDA, focus on technical indicators"
- 🔧 Real-time parameter adjustments

#### UI Version Example Conversation

```
User: "Please analyze NVDA's investment opportunity, I'm interested in short-term technical indicators"

System:
✓ Understood your requirements
✓ Launching analysts: Market Analyst, Fundamentals Analyst
✓ Analysis timeframe: Recent
✓ Focus: Technical indicators

[Starting analysis report generation...]
[Displaying visualization charts...]

User: "Can you add news sentiment analysis?"

System:
✓ Added News Analyst
✓ Re-running analysis...
[Updating report...]
```

**Detailed Documentation**:
- `README_INTERACTIVE.md` - Complete interactive mode guide
- `QUICK_START_INTERACTIVE.md` - UI version quick start
- `INTERACTIVE_USAGE.md` - Detailed usage instructions

---

## 📋 Version Selection Guide

### 🤔 Which Version Should I Choose?

**If you are...**

👨‍💻 **Developer/Technical User** → Choose **Main Branch**
- Familiar with command line operations
- Need complete OpenAI GPT-4 support
- Want standardized analysis workflow

🏢 **Enterprise User/WatsonX Customer** → Choose **WatsonX Branch**
- Already have IBM WatsonX.ai account
- Need enterprise-grade AI models
- Require private deployment or data compliance

🌟 **Investor/Analyst/New User** → Choose **UI-version Branch** ⭐
- Not familiar with command line operations
- Prefer chat interface interaction
- Need visualized analysis process
- Want to get started quickly

### 💡 Feature Comparison

| Feature | Main Branch | WatsonX Branch | UI-version Branch |
|---------|-------------|----------------|-------------------|
| Single Stock Analysis | ✅ | ✅ | ✅ |
| Portfolio Analysis | ✅ | ✅ | ✅ |
| OpenAI GPT-4 | ✅ | ✅ | ✅ |
| IBM WatsonX.ai | ❌ | ✅ | ✅ |
| Command Line Interface | ✅ | ✅ | ✅ |
| Web Interface | ❌ | ❌ | ✅ |
| Interactive Chat | ❌ | ❌ | ✅ |
| Real-time Feedback | ❌ | ❌ | ✅ |
| Visualization Dashboard | ❌ | ❌ | ✅ |

---

## 🎬 Demo Video

[![TradingAgents Demo](https://img.youtube.com/vi/3vmgWtg3G60/0.jpg)](https://youtu.be/3vmgWtg3G60?feature=shared)

Watch our comprehensive demo showcasing the multi-agent analysis workflow and portfolio optimization capabilities.

---

## 🏛️ System Overview

TradingAgents Enhanced Edition is an **AI Investment Assistant System** that provides professional-grade market analysis and investment recommendations through multi-agent collaboration.

### 🎯 Core Capabilities

- **📊 Institutional-Grade Analysis**: Simulates investment committee with multi-perspective evaluation
- **🤖 AI Agent Teams**: Market analysts, fundamental analysts, news analysts, and specialized teams
- **📈 Quantitative Optimization**: Kelly Criterion, VaR/CVaR risk management, 6 optimization strategies
- **📑 Professional Reports**: Auto-generated Word/Markdown format professional analysis reports

### ⚠️ Important Disclaimer

The reports, charts, and recommendations generated by this system are designed to **assist and support your investment decisions**, not replace your judgment. All analysis should be considered educational and decision-support material. Always conduct your own research and consider your personal financial situation before making investment decisions.

---

## 🏗️ System Architecture

### Overall Architecture
![Overall Architecture](docs/overall%20architecture.png)

### User Workflow
![User Workflow](docs/user%20workflow.png)

<details>
<summary><b>📊 Click to view detailed analyst architectures</b></summary>

### Individual Analyst Architectures

#### Market Analyst Architecture
![Market Analyst Architecture](docs/market%20analyst%20architecture.png)

#### Fundamental Analyst Architecture
![Fundamental Analyst Architecture](docs/fundamental%20analyst%20architecture.png)

#### News Analyst Architecture
![News Analyst Architecture](docs/news%20analyst%20architecture.png)

#### Quantitative Analyst Architecture
![Quantitative Analyst Architecture](docs/quantatative%20analyst%20architecture.png)

#### Portfolio Analyst Architecture
![Portfolio Analyst Architecture](docs/portofolio%20anaylst%20architecture.png)

### Portfolio System Architecture

#### Multi-Scenario Optimization Architecture
![Multi-Scenario Optimization Architecture](docs/multi-scenario%20optimization%20architecture.png)

#### Multi-Stock Portfolio Generation System
![Multi-Stock Portfolio Generation System](docs/multi-stock%20portofolio%20generation%20system.png)

</details>

---

## 📊 Analysis Results Preview

**Want to see what this system can do?** Check out our latest analysis examples:

### Single Stock Analysis Examples (2025-10-09)
- **AAPL Analysis**: [`results/AAPL/2025-10-09/`](results/AAPL/2025-10-09/) - Complete analysis reports, charts, CSV data
- **NVDA Analysis**: [`results/NVDA/2025-10-09/`](results/NVDA/2025-10-09/) - Comprehensive technical and fundamental analysis

### Portfolio Analysis Examples
- **Multi-Stock Portfolio**: [`portfolio_results/2025-10-09/portfolio_analysis_2025-10-09.md`](portfolio_results/2025-10-09/portfolio_analysis_2025-10-09.md) - Advanced portfolio optimization and allocation recommendations

---

## ⚙️ Advanced Configuration

<details>
<summary><b>🔧 Click to view detailed configuration options</b></summary>

### Analysis Mode Configuration (main_enterprise.py)

```python
# Analysis scope
portfolio_mode = False  # True: Multi-stock portfolio | False: Single stock
portfolio_tickers = ["NVDA", "AAPL", "MSFT", "GOOGL"]  # Portfolio stock list
company_of_interest = "NVDA"  # Single stock analysis target
current_date = "2025-10-09"  # Analysis date
```

### AI Analyst Team Selection

```python
selected_analysts = [
    "market",                    # 📈 Technical Analysis: RSI, MACD, Bollinger Bands
    "fundamentals",              # 💰 Financial Analysis: P/E, Revenue, Cash Flow
    "news",                      # 📰 News Sentiment: Headline analysis, Impact assessment
    "social",                    # 🐦 Social Media: Reddit, Twitter sentiment
    "comprehensive_quantitative", # 🔬 Advanced ML: GARCH models, Statistical forecasting
    "portfolio",                 # 📊 Portfolio Impact: Correlation analysis, Sector diversification
    "enterprise_strategy"        # 🏛️ Strategic Analysis: Long-term positioning, Institutional perspective
]

# Quick analysis configuration (faster, less resources)
selected_analysts = ["market", "fundamentals"]
```

### LLM Model Configuration

```python
config = {
    # OpenAI configuration
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o",        # Complex analysis
    "quick_think_llm": "gpt-4o-mini",  # Fast operations

    # WatsonX configuration
    # "llm_provider": "watsonx",
    # "deep_think_llm": "mistralai/mixtral-8x7b-instruct-v01",

    # Analysis depth
    "enterprise_mode": True,              # Enterprise-grade features
    "max_debate_rounds": 2,               # Bull/Bear debate rounds
    "lightweight_quantitative": False,    # Full optimization algorithms
}
```

### Pre-configured Scenarios

**Scenario 1: Quick Personal Investment Analysis**
```python
selected_analysts = ["market", "fundamentals"]
config = {
    "deep_think_llm": "gpt-4o-mini",
    "max_debate_rounds": 1,
    "lightweight_quantitative": True
}
```

**Scenario 2: Professional Advisor Reports**
```python
selected_analysts = ["market", "fundamentals", "news", "social", "comprehensive_quantitative"]
config = {
    "deep_think_llm": "gpt-4o",
    "enterprise_mode": True,
    "max_debate_rounds": 2
}
```

**Scenario 3: Institutional Investment Committee**
```python
selected_analysts = [
    "market", "fundamentals", "news", "social",
    "comprehensive_quantitative", "portfolio", "enterprise_strategy"
]
config = {
    "deep_think_llm": "gpt-4o",
    "enterprise_mode": True,
    "max_debate_rounds": 3,
    "max_risk_discuss_rounds": 3
}
```

</details>

---

## 📁 Project Structure

<details>
<summary><b>📂 Click to view complete directory structure</b></summary>

```
TradingAgents-main/
├── main_enterprise.py              # Main entry point (OpenAI)
├── main_enterprise_watsonx.py      # WatsonX version entry (WatsonX branch)
├── flask_chat_app.py               # Flask Web UI (UI-version branch)
├── main_interactive_watsonx.py     # Interactive WatsonX (UI-version branch)
├── single_stock_analysis.py        # Lightweight single stock analysis
├── run_portfolio_analysis.py       # Standalone portfolio analysis
│
├── tradingagents/                  # Core system package
│   ├── agents/                    # AI agents
│   │   ├── analysts/              # Analyst teams
│   │   │   ├── market_analyst.py
│   │   │   ├── fundamentals_analyst.py
│   │   │   ├── news_analyst.py
│   │   │   ├── comprehensive_quantitative_analyst.py
│   │   │   ├── portfolio_analyst.py
│   │   │   └── visualizer_analyst.py  # UI version addition
│   │   ├── traders/               # Trading decisions
│   │   ├── researchers/           # Research teams
│   │   ├── managers/              # Management coordination
│   │   └── generators/            # Report generation
│   │
│   ├── interactive/               # Interactive system (UI-version branch)
│   │   ├── gradio_ui.py           # Gradio interface
│   │   ├── simple_chat_ui.py      # Simple chat interface
│   │   ├── interactive_workflow.py # Interactive workflow
│   │   └── user_preference_parser.py
│   │
│   ├── graph/                     # LangGraph workflow
│   │   ├── trading_graph.py
│   │   ├── setup.py
│   │   └── conditional_logic.py
│   │
│   ├── portfolio/                 # Portfolio system
│   │   ├── stock_data_aggregator.py
│   │   ├── multi_scenario_portfolio_optimizer.py
│   │   └── portfolio_report_generator.py
│   │
│   └── dataflows/                 # Data flows
│       ├── yfin_utils.py          # Yahoo Finance
│       ├── finnhub_utils.py       # Finnhub API
│       └── googlenews_utils.py    # News scraping
│
├── results/                       # Analysis results
│   └── {TICKER}/{DATE}/
│       ├── {TICKER}_comprehensive_analysis_{DATE}.md
│       ├── {TICKER}_comprehensive_analysis_{DATE}.docx
│       ├── {TICKER}_comprehensive_analysis_{DATE}.png
│       └── csv_data/              # 6 CSV files
│
├── portfolio_results/             # Portfolio analysis results
│   └── {DATE}/portfolio_analysis_{DATE}.md
│
├── static/                        # Web UI static files (UI-version)
│   └── chat.html
│
└── docs/                          # Architecture diagrams and docs
    ├── overall architecture.png
    ├── user workflow.png
    └── ...
```

</details>

---

## 🔧 Troubleshooting

### Common Issues

<details>
<summary><b>1. API Key Error</b></summary>

```bash
# Ensure correct API Key is set
export OPENAI_API_KEY="your-key-here"

# OR WatsonX
export WATSONX_APIKEY="your-watsonx-key"
export WATSONX_PROJECT_ID="your-project-id"

# Windows users
set OPENAI_API_KEY=your-key-here
```
</details>

<details>
<summary><b>2. Dependency Installation Issues</b></summary>

```bash
# Reinstall dependencies
uv sync --reinstall

# OR use pip
pip install -r requirements.txt --force-reinstall
```
</details>

<details>
<summary><b>3. Portfolio Analysis Fails</b></summary>

```bash
# Ensure single stock analyses are completed
# Check if CSV files exist
ls results/{TICKER}/{DATE}/csv_data/

# Need at least 2 stocks with complete analysis results
```
</details>

<details>
<summary><b>4. Web UI Won't Start (UI-version branch)</b></summary>

```bash
# Check if port is in use
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac

# Change port
# Edit flask_chat_app.py, modify port=5000 to another port
```
</details>

<details>
<summary><b>5. Memory Issues</b></summary>

```python
# Reduce number of analysts
selected_analysts = ["market", "fundamentals"]

# Use lightweight configuration
config = {
    "lightweight_quantitative": True,
    "max_debate_rounds": 1
}
```
</details>

### Log File Locations

- Main log: `enterprise_output.log`
- WatsonX log: `enterprise_watsonx_output.log`
- Agent logs: `eval_results/{TICKER}/TradingAgentsStrategy_logs/`

---

## 🛣️ Development Roadmap

### ✅ Completed
- ✅ Single stock analysis system
- ✅ Portfolio optimization
- ✅ IBM WatsonX.ai integration (watsonx-integration branch)
- ✅ Interactive Web UI (UI-version branch)
- ✅ Multi-LLM support (OpenAI + WatsonX)

### 🚧 In Progress
- 🚧 Enhanced portfolio visualization
- 🚧 Mobile responsive design
- 🚧 Real-time data streaming integration

### 📋 Planned
- 📋 Backtesting engine
- 📋 RESTful API
- 📋 Claude AI integration
- 📋 Local model support (Llama, Mistral)

---

## 🤝 Contributing

Welcome contributions to TradingAgents Enhanced Edition!

### Priority Areas
- **Interactive Interface Improvements**: UI/UX enhancements
- **Multi-language Support**: Internationalization
- **Test Coverage**: Unit and integration tests
- **Documentation**: User guides and API documentation

### How to Contribute
1. Fork the repository
2. Choose the appropriate branch to work on
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Create a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Based on [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents.git) original architecture
- IBM WatsonX.ai team for LLM integration support
- OpenAI for GPT-4 API access
- Open-source financial analysis community

---

## 📞 Support

- 💬 **Issues**: [GitHub Issues](https://github.com/ZhaoYiping789/tradingagent_enhanced/issues)
- 📧 **Email**: Please submit project-related questions via GitHub Issues
- 📚 **Documentation**: Check README and quick start guides in each branch

---

**TradingAgents Enhanced Edition** - Next-generation AI-driven trading analysis system with institutional-grade quantitative methods and multi-LLM support.

*⭐ Three Professional Versions Available | 🚀 Actively Developed | 🤝 Community Contributions Welcome*
