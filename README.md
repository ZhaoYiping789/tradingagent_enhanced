# TradingAgents Enhanced Edition - Interactive Web UI Version

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Web-Flask-green)](https://flask.palletsprojects.com/)
[![LangChain](https://img.shields.io/badge/Built%20with-LangChain-green)](https://www.langchain.com/)

**AI-Powered Investment Analysis with Interactive Web Chat Interface**

Chat with AI agents through a modern web interface to analyze stocks, build portfolios, and get institutional-grade investment recommendations.

---

## 🌟 What is This?

This is the **Interactive Web UI Version** of TradingAgents Enhanced Edition - an AI-powered multi-agent investment analysis system that you can use through your web browser with a ChatGPT-style interface.

### ✨ Key Features

- 🖥️ **Modern Flask Chat Interface** - Beautiful web UI, no command line needed
- 💬 **Natural Conversation** - Chat with AI agents like ChatGPT
- 📊 **Real-time Visualization** - See charts and analysis as they're generated
- 🔄 **Iterative Analysis** - Refine results through follow-up questions
- 🎯 **Smart Agent Selection** - AI automatically chooses the right analysts
- 🤖 **Multi-LLM Support** - Works with OpenAI GPT-4 and IBM WatsonX
- 📈 **Professional Reports** - Download Word/PDF reports

---

## 🚀 Quick Start - 3 Simple Steps

### Step 1: Install Dependencies with UV

**First, make sure you have UV package manager:**

```bash
# Install UV if you don't have it
pip install uv

# Navigate to the project directory
cd tradingagent_enhanced

# Install all dependencies
uv sync
```

**This is IMPORTANT:** `uv sync` will set up the complete environment with all required packages.

### Step 2: Set Your API Key

**Option A: Using OpenAI (Recommended for most users)**

```bash
# Windows
set OPENAI_API_KEY=your-openai-api-key-here

# Linux/Mac
export OPENAI_API_KEY="your-openai-api-key-here"
```

Get your API key from: https://platform.openai.com/api-keys

**Option B: Using IBM WatsonX (Enterprise users)**

```bash
# Windows
set WATSONX_APIKEY=your-watsonx-api-key
set WATSONX_PROJECT_ID=your-project-id
set WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Linux/Mac
export WATSONX_APIKEY="your-watsonx-api-key"
export WATSONX_PROJECT_ID="your-project-id"
export WATSONX_URL="https://us-south.ml.cloud.ibm.com"
```

### Step 3: Launch the Web UI

**Start the Flask server:**

```bash
uv run flask_chat_app.py
```

You should see:
```
======================================================================
AI Trading Analysis - Flask Chat Interface
======================================================================

[OK] WatsonX configuration loaded
[MODEL] meta-llama/llama-3-3-70b-instruct

[INFO] Starting Flask server...
[INFO] Open your browser to: http://localhost:7862
```

**Then open your browser to:** **http://localhost:7862**

That's it! You're ready to analyze stocks.

---

## 💬 How to Use - Interactive Chat Examples

### Example 1: Simple Stock Analysis

**You type:**
```
Analyze NVDA for short-term trading
```

**System responds:**
```
✓ Understanding your request...
✓ Stock: NVDA
✓ Focus: Short-term trading
✓ Launching: Market Analyst, News Analyst

[Real-time progress updates...]

📊 Technical Analysis Complete
📰 News Sentiment Analysis Complete
📈 Generating comprehensive report...

[Beautiful formatted report with charts appears]
```

### Example 2: Portfolio Analysis

**You type:**
```
Build a portfolio with NVDA, AAPL, and MSFT focusing on risk management
```

**System responds:**
```
✓ Portfolio mode activated
✓ Stocks: NVDA, AAPL, MSFT
✓ Focus: Risk management
✓ Analyzing each stock...

[Progress for each stock shown]

📊 Running portfolio optimization...
  ✓ Kelly Criterion
  ✓ Risk Parity
  ✓ Minimum Variance

💡 AI Portfolio Manager deciding allocation...

[Final allocation with detailed reasoning]
```

### Example 3: Follow-up Questions

**You type:**
```
Can you add social media sentiment to this analysis?
```

**System responds:**
```
✓ Adding Social Media Analyst
✓ Re-running analysis with sentiment data...

[Updated report with social sentiment]
```

**You type:**
```
What if the market crashes? Show me a conservative allocation.
```

**System responds:**
```
✓ Adjusting risk profile to conservative
✓ Re-optimizing portfolio...

[New conservative allocation shown]
```

---

## 🎨 Web Interface Features

### Flask Chat UI

**URL:** http://localhost:7862

**Interface Components:**

- **💬 Chat Window**: Scrollable conversation history with your analyses
- **📝 Input Box**: Bottom text area for typing your requests
- **📤 Send Button**: Submit your message (or press Enter)
- **📊 Embedded Charts**: Analysis charts appear directly in chat
- **📥 Export Button**: Download reports as Word/PDF
- **🗑️ Clear Chat**: Start a fresh conversation
- **⚙️ Status Indicator**: Shows when analysis is running

**Features:**
- Real-time streaming responses
- Markdown-formatted reports with syntax highlighting
- Persistent chat history (saved locally)
- Mobile-responsive design
- Dark/light mode support

**How It Works:**
1. Type your request naturally (e.g., "Analyze TSLA", "Build portfolio with tech stocks")
2. AI parses your intent and selects appropriate analysts
3. Watch real-time progress as agents work
4. Review comprehensive report with charts and tables
5. Ask follow-up questions to refine analysis
6. Download final reports when satisfied

---

## 🛠️ Advanced Configuration

### Customizing Analysis

Edit `flask_chat_app.py` (around line 75-80) to customize default analysts:

```python
graph = TradingAgentsGraph(
    selected_analysts=[
        "market",                    # Technical analysis (RSI, MACD, etc.)
        "fundamentals",              # Financial metrics (P/E, revenue, etc.)
        "news",                      # News sentiment analysis
        "social",                    # Social media sentiment
        "quantitative",              # Statistical models
        "comprehensive_quantitative", # Advanced ML models
        "visualizer"                 # Chart generation
    ],
    debug=False,
    config=WATSONX_CONFIG  # or OPENAI_CONFIG
)
```

### Using OpenAI Instead of WatsonX

Change configuration in `flask_chat_app.py` (around line 34-47):

```python
# OpenAI Configuration
OPENAI_CONFIG = {
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o",        # For complex analysis
    "quick_think_llm": "gpt-4o-mini",  # For fast operations
    "max_debate_rounds": 2,
    "enterprise_mode": True,
    "online_tools": True,
}
```

### Performance Tuning

**For Faster Analysis:**
```python
selected_analysts = ["market", "fundamentals"]  # Use fewer analysts
config["lightweight_quantitative"] = True
config["max_debate_rounds"] = 1
```

**For Comprehensive Analysis:**
```python
selected_analysts = ["market", "fundamentals", "news", "social",
                    "comprehensive_quantitative", "portfolio", "enterprise_strategy"]
config["max_debate_rounds"] = 3
config["lightweight_quantitative"] = False
```

---

## 📚 Available Project Branches

This repository has multiple versions:

| Branch | Description | Best For |
|--------|-------------|----------|
| **main** (this one) | Interactive Flask Web UI | All users, easiest to use |
| **watsonx-integration** | IBM WatsonX CLI + Web | Enterprise WatsonX users |
| **cli-version** | Command-line only (OpenAI) | Developers, automation |

**To switch branches:**
```bash
# For WatsonX CLI version
git checkout watsonx-integration

# For pure CLI version
git checkout cli-version

# Back to Web UI
git checkout main
```

---

## 🔧 Troubleshooting

### Issue: JSON Parse Error / 500 Internal Server Error

**Symptom:** `Unexpected token '<', "<!doctype "... is not valid JSON`

**Cause:** Multiple old Flask processes running on the same port

**Solution:**
```bash
# Windows - Find and kill processes on port 7862
netstat -ano | findstr :7862
taskkill /F /PID <process_id>

# Linux/Mac
lsof -i :7862
kill -9 <process_id>

# Then restart clean
uv run flask_chat_app.py
```

### Issue: Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Change port in flask_chat_app.py (line 1928)
app.run(host='0.0.0.0', port=7862, debug=False)
# Change 7862 to another port like 8080
```

### Issue: API Key Not Working

**Error:** `Authentication failed`

**Solution:**
```bash
# Verify key is set
echo %OPENAI_API_KEY%  # Windows
echo $OPENAI_API_KEY   # Linux/Mac

# Key must be active and have credits
# Test at: https://platform.openai.com/api-keys
```

### Issue: Dependencies Missing

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
# Reinstall all dependencies
uv sync --reinstall

# Or use pip
pip install -r requirements.txt --force-reinstall
```

### Issue: Analysis Takes Too Long

**Solution:**
```python
# In flask_chat_app.py, reduce analysts:
selected_analysts = ["market", "fundamentals"]  # Minimal set

# Or use lightweight mode
config["lightweight_quantitative"] = True
config["max_debate_rounds"] = 1
```

### Issue: Charts Not Displaying

**Solution:**
- Ensure `matplotlib` is installed: `pip install matplotlib`
- Clear browser cache (Ctrl + Shift + R)
- Check browser console (F12) for errors
- Try different browser

---

## 📁 Output Files Location

All analysis results are automatically saved:

### Single Stock Analysis

**Location:** `results/{TICKER}/{DATE}/`

**Files:**
- `{TICKER}_comprehensive_analysis_{DATE}.md` - Markdown report
- `{TICKER}_comprehensive_analysis_{DATE}.docx` - Word document
- `{TICKER}_comprehensive_analysis_{DATE}.png` - Technical charts
- `csv_data/` - 6 CSV files with structured data:
  - `summary_metrics.csv`
  - `risk_metrics.csv`
  - `technical_indicators.csv`
  - `financial_metrics.csv`
  - `optimization_scenarios.csv`
  - `sentiment_analysis.csv`

### Portfolio Analysis

**Location:** `portfolio_results/{DATE}/`

**Files:**
- `portfolio_analysis_{DATE}.md` - Comprehensive portfolio report
- Individual stock CSV data aggregated

---

## 🎯 Pro Tips for Best Results

### 1. Be Specific in Your Requests

```
❌ Bad:  "Analyze NVDA"
✅ Good: "Analyze NVDA for swing trading, focus on technical indicators and recent news"
```

### 2. Use Natural Language

```
"I want to invest $10k in tech stocks with moderate risk"
"Compare NVDA and AMD for gaming GPU market exposure"
"Build a defensive portfolio for retirement"
```

### 3. Ask Follow-up Questions

```
"What if interest rates rise?"
"Show me a more aggressive allocation"
"What are the key risks I should worry about?"
"How does this compare to last quarter?"
```

### 4. Iterate and Refine

```
1. Start: "Quick analysis of TSLA"
2. Review initial report
3. Refine: "Add news sentiment and social media analysis"
4. Review updated report
5. Finalize: "Generate final recommendation with risk assessment"
```

### 5. Use Portfolio Mode Effectively

```
"Build a portfolio with NVDA, AAPL, MSFT, GOOGL"
→ System analyzes each stock individually
→ Then runs 6 portfolio optimization strategies
→ AI makes final allocation decision with reasoning
```

---

## 🔐 Security & Privacy

### Data Handling

- ✅ Chat history stored **locally only** (not sent anywhere)
- ✅ API keys never logged or transmitted (except to LLM providers)
- ✅ Analysis results saved **only on your machine**
- ✅ No telemetry or tracking
- ✅ No data sent to third parties except LLM APIs

### Using OpenAI

- Data sent to OpenAI per their [privacy policy](https://openai.com/policies/privacy-policy)
- API calls can be opted out of training data
- Secure HTTPS communication
- No data persistence after API call (with proper settings)

### Using WatsonX

- Enterprise-grade security and compliance
- Data stays within IBM infrastructure
- GDPR, SOC 2, HIPAA ready
- Full audit trails available
- Custom deployment options

---

## 📞 Support & Documentation

### Getting Help

- 💬 **GitHub Issues**: [Report bugs or request features](https://github.com/ZhaoYiping789/tradingagent_enhanced/issues)
- 📖 **Documentation**:
  - `INTERACTIVE_USAGE.md` - Detailed usage guide
  - `QUICK_START_INTERACTIVE.md` - Quick reference
  - `README_INTERACTIVE.md` - Feature explanations
- 📧 **Questions**: Use GitHub Issues for technical questions

### Additional Resources

**For WatsonX Users:**
- `README_WATSONX.md` - Complete WatsonX integration guide
- `QUICK_START_WATSONX.md` - WatsonX quick start
- `WATSONX_SETUP.md` - Detailed WatsonX configuration

**For CLI Users:**
- Switch to `cli-version` branch for command-line documentation

---

## ⚠️ Important Disclaimer

**This system is for educational and decision-support purposes only.**

The analysis, reports, and recommendations generated by this AI system are designed to **assist your investment research** - NOT replace it.

**Always:**
- ✅ Conduct your own independent research
- ✅ Consult with qualified financial advisors
- ✅ Consider your personal financial situation and risk tolerance
- ✅ Understand the risks of investing
- ❌ **Never invest money you cannot afford to lose**
- ❌ **Don't make decisions based solely on AI recommendations**

**Past performance does not guarantee future results.** Stock markets are inherently risky and unpredictable.

---

## 🤝 Contributing

We welcome contributions!

### Priority Areas

- 🎨 **UI/UX improvements** - Make the interface even better
- 🌐 **Multi-language support** - Internationalization
- 📱 **Mobile optimization** - Better mobile experience
- 🧪 **Testing** - Unit tests and integration tests
- 📖 **Documentation** - Improve guides and examples

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with clear commits
4. Test thoroughly
5. Push to your fork (`git push origin feature/amazing-feature`)
6. Open a Pull Request with description

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Based on [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents.git) architecture
- Powered by OpenAI GPT-4 and IBM WatsonX
- Built with LangChain, Flask, and LangGraph
- Community contributions appreciated

---

## 🚀 What's Next?

### Current Features
- ✅ Interactive Flask web chat interface
- ✅ Multi-LLM support (OpenAI + WatsonX)
- ✅ Real-time analysis with progress updates
- ✅ Portfolio optimization with 6+ strategies
- ✅ Professional report generation

### Coming Soon
- 🚧 Mobile app version
- 🚧 Real-time market data streaming
- 🚧 Advanced backtesting engine
- 📋 Social sharing features
- 📋 Custom indicator builder
- 📋 REST API for developers
- 📋 Trading strategy backtester

---

**TradingAgents Enhanced Edition - Interactive Web UI Version**

*🌐 Chat-Based Analysis | 🤖 Multi-Agent AI | 📊 Institutional-Grade Reports*

**Ready to start?**

```bash
uv sync
uv run flask_chat_app.py
```

Then open **http://localhost:7862** in your browser.

**Questions?** Open an issue on GitHub.

**Find this useful?** Star us on GitHub! ⭐
