# TradingAgents Enhanced Edition - IBM WatsonX Integration

[![WatsonX Powered](https://img.shields.io/badge/Powered%20by-IBM%20WatsonX-blue)](https://www.ibm.com/watsonx)
[![LangChain](https://img.shields.io/badge/Built%20with-LangChain-green)](https://www.langchain.com/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

**Enterprise-Grade AI Investment Assistant powered by IBM WatsonX AI Platform**

This is a specialized version of [TradingAgents Enhanced Edition](https://github.com/ZhaoYiping789/tradingagent_enhanced) that has been fully integrated with **IBM WatsonX AI**, providing enterprise-level AI capabilities with advanced governance, security, and compliance features.

---

## 🌟 What Makes This WatsonX Version Special?

### IBM WatsonX AI Platform Integration

This version leverages IBM's enterprise AI platform to provide:

- **🏢 Enterprise-Grade AI Models**: Access to IBM's curated foundation models including:
  - `meta-llama/llama-3-3-70b-instruct` for deep analysis
  - `ibm/granite-3-3-8b-instruct` for fast processing

- **🔒 Enterprise Security & Governance**: WatsonX provides:
  - Built-in AI governance and compliance tracking
  - Secure model deployment with audit trails
  - Data privacy and protection controls

- **📊 Advanced Embeddings**: WatsonX embeddings for efficient document retrieval

- **⚡ Flexible Deployment**: Works in both IBM Cloud and on-premise environments

---

## 🚀 Key Features

### Multi-Agent AI Investment Analysis System

Our WatsonX-powered system provides institutional-grade investment analysis through specialized AI agents:

#### 7 Specialized Analyst Agents

1. **📊 Market Analyst** - Technical indicators and price action analysis
2. **📰 News Analyst** - Real-time news sentiment using Google News API
3. **💼 Fundamental Analyst** - Company financials and valuation metrics
4. **📈 Quantitative Analyst** - Mathematical models and risk assessment
5. **🎯 Portfolio Analyst** - Multi-stock portfolio optimization
6. **🏛️ Enterprise Strategy Analyst** - Long-term strategic assessment
7. **🤖 Portfolio Trader** - Final allocation decisions with AI reasoning

#### Advanced Portfolio Management

- **🎲 Multi-Scenario Optimization**: 6 different optimization strategies
  - Maximum Sharpe Ratio (Risk-Adjusted Returns)
  - Minimum Variance (Risk Minimization)
  - Risk Parity (Equal Risk Contribution)
  - Maximum Diversification
  - Hierarchical Risk Parity (HRP)
  - Kelly Criterion-based Position Sizing

- **📊 Comprehensive Risk Analysis**:
  - Value at Risk (VaR) at 95% confidence
  - Conditional Value at Risk (CVaR)
  - Maximum Drawdown calculations
  - GARCH volatility forecasting

- **🤖 AI Portfolio Manager**: LLM-powered final allocation decisions

---

## 📋 Prerequisites

### Required

1. **Python 3.10 or higher**
2. **IBM WatsonX Account** with:
   - WatsonX API Key
   - WatsonX Project ID
   - WatsonX URL (default: `https://us-south.ml.cloud.ibm.com`)
3. **UV Package Manager** (recommended) or pip

---

## 🔧 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/ZhaoYiping789/tradingagent_enhanced.git
cd tradingagent_enhanced
git checkout watsonx-integration  # Switch to WatsonX branch
```

### Step 2: Install Dependencies

**Using UV (Recommended):**
```bash
pip install uv
uv pip install -r requirements.txt
```

### Step 3: Configure WatsonX Credentials

Create a `.env` file or set environment variables:

```bash
# WatsonX Configuration
export WATSONX_APIKEY="your-watsonx-api-key"
export WATSONX_PROJECT_ID="your-project-id"
export WATSONX_URL="https://us-south.ml.cloud.ibm.com"
```

### Step 4: Verify Installation

```bash
python test_watsonx_connection.py
```

---

## 🎯 Usage Guide

### Option 1: Single Stock Analysis

```bash
# Analyze NVDA using WatsonX
uv run main_enterprise_watsonx.py
```

### Option 2: Multi-Stock Portfolio Analysis

```bash
# Portfolio analysis for NVDA and AAPL
uv run run_portfolio_watsonx.py
```

**Sample Output:**
```
🤖 Calling Portfolio Manager LLM for final allocation decision...
✅ LLM Portfolio Manager decision received:
   - NVDA: 67.30%
   - AAPL: 32.70%

📊 Confidence Level: 8/10
🎯 Time Horizon: 6-12 months
```

### Option 3: Web Interface

```bash
uv run web_ui.py
```

Then open: **http://localhost:5000**

---

## 📈 Sample Results

### Portfolio Analysis Output

**Section 5: WatsonX LLM Final Allocation Decision** ⭐

```markdown
**FINAL RECOMMENDED ALLOCATION:**
- NVDA: 67.30%
- AAPL: 32.70%

**Portfolio Manager Detailed Analysis:**
After analyzing individual stock analysis, quantitative optimization results,
and market context, I have decided to allocate 67.3% to NVDA and 32.7% to AAPL.
NVDA's strong fundamental analysis combined with positive technical momentum...

**Confidence Level:** 8/10
**Time Horizon:** 6-12 months
**Preferred Optimization Approach:** Modified Maximum Sharpe with risk adjustments

**Key Decision Factors:**
- Strong fundamental analysis of NVDA
- Bullish sentiment of NVDA
- Higher expected return and Sharpe ratio of NVDA
- Moderate volatility in the tech environment
```

---

## 🔍 Troubleshooting

### Issue: WatsonX Connection Failed

```
❌ ERROR: Authentication failed
```

**Solution:**
1. Verify your WatsonX credentials
2. Check your WatsonX project has model access
3. Verify URL is correct for your region

### Issue: Portfolio Trader LLM Not Called

**Solution:**
- Fixed in `portfolio_report_generator.py:38`
- Make sure you're using the latest version from `watsonx-integration` branch

---

## 🔒 Security & Compliance

### WatsonX Enterprise Benefits

1. **Data Privacy**: Your data stays within IBM's secure infrastructure
2. **Audit Trails**: All AI decisions are logged and traceable
3. **Compliance**: GDPR, SOC 2, HIPAA ready
4. **Governance**: AI model usage tracking and monitoring

---

## 📊 Performance Benchmarks

### Analysis Time (Single Stock)

| Component | Time | Notes |
|-----------|------|-------|
| Market Analysis | 2-3 min | Technical indicators |
| News Analysis | 3-5 min | Google News API |
| Fundamental Analysis | 2-3 min | Financial metrics |
| Quantitative Analysis | 5-7 min | Optimization models |
| **Total** | **20-30 min** | Full enterprise analysis |

---

## 🎯 Quick Start Checklist

- [ ] Install Python 3.10+
- [ ] Get WatsonX credentials (API key, Project ID)
- [ ] Clone repository and checkout `watsonx-integration` branch
- [ ] Install dependencies with UV or pip
- [ ] Set environment variables
- [ ] Run `test_watsonx_connection.py` to verify
- [ ] Try single stock analysis: `uv run main_enterprise_watsonx.py`
- [ ] Try portfolio analysis: `uv run run_portfolio_watsonx.py`
- [ ] Launch web UI: `uv run web_ui.py`

---

**⚠️ Disclaimer**: This system is for educational and decision-support purposes only. Always conduct your own research and consult with financial advisors before making investment decisions.

---

**Made with ❤️ using IBM WatsonX AI Platform**
