# Quick Start Guide - WatsonX Integration

This guide will get you up and running with TradingAgents using IBM WatsonX.ai in 5 minutes.

## Prerequisites

- Python 3.10+
- UV package manager installed
- Your WatsonX credentials (already configured)

## Step 1: Setup Environment (2 minutes)

### Option A: Automated Setup (Windows)

```bash
# Run the setup script
setup_watsonx_env.bat
```

### Option B: Manual Setup

```bash
# Create WatsonX environment
uv venv watsonx_env

# Activate environment
watsonx_env\Scripts\activate

# Install dependencies
uv pip install langchain-ibm ibm-watsonx-ai
uv sync
```

## Step 2: Set Environment Variables (1 minute)

### Windows (Recommended)

```bash
# Run the environment variable script
set_watsonx_env.bat
```

Or set manually:

```bash
set WATSONX_URL=https://us-south.ml.cloud.ibm.com
set WATSONX_APIKEY=1NlP-L5h1DDEZFKkvJ92uTuMFNbkk0pmGJ4lMutJ44w2
set WATSONX_PROJECT_ID=394811a9-3e1c-4b80-8031-3fda71e6dce1
```

### Linux/Mac

```bash
export WATSONX_URL=https://us-south.ml.cloud.ibm.com
export WATSONX_APIKEY=1NlP-L5h1DDEZFKkvJ92uTuMFNbkk0pmGJ4lMutJ44w2
export WATSONX_PROJECT_ID=394811a9-3e1c-4b80-8031-3fda71e6dce1
```

## Step 3: Test Connection (1 minute)

```bash
# Run connection test
python test_watsonx_connection.py
```

Expected output:
```
✅ WATSONX_URL: https://us-south.ml.cloud.ibm.com
✅ WATSONX_PROJECT_ID: 394811a9-3e1c-4b80-8031-3fda71e6dce1
✅ langchain-ibm is installed
✅ WatsonX LLM initialized successfully
✅ ALL TESTS PASSED!
```

## Step 4: Run Your First Analysis (1 minute)

```bash
# Analyze a single stock (NVDA)
python main_enterprise_watsonx.py
```

The analysis will:
- Use all 7 specialized AI analysts
- Generate comprehensive reports in Markdown and Word formats
- Create technical analysis charts
- Export structured CSV data
- Provide BUY/SELL/HOLD recommendation

## What to Expect

**Analysis Time**: 3-5 minutes for single stock
**Output Location**: `results/NVDA/2025-10-10/`

**Generated Files**:
- `NVDA_comprehensive_analysis_2025-10-10.md` - Markdown report
- `NVDA_comprehensive_analysis_2025-10-10.docx` - Word document
- `NVDA_comprehensive_analysis_2025-10-10.png` - Technical charts
- `csv_data/` - 6 CSV files with structured metrics

## Customization

### Change Stock Symbol

Edit `main_enterprise_watsonx.py` line 137:

```python
ticker = "AAPL"  # Change to any stock symbol
```

### Analyze Portfolio (Multiple Stocks)

Edit `main_enterprise_watsonx.py` lines 135-136:

```python
portfolio_mode = True  # Enable portfolio mode
portfolio_tickers = ["NVDA", "AAPL", "MSFT", "GOOGL"]
```

### Select Fewer Analysts (Faster Analysis)

Edit `main_enterprise_watsonx.py` lines 92-99:

```python
selected_analysts = [
    "market",       # Technical analysis only
    "fundamentals"  # Fundamental analysis only
]
```

### Change Model

Edit `main_enterprise_watsonx.py` lines 84-85:

```python
# Options:
# - mistralai/mixtral-8x7b-instruct-v01 (Best for tool calling)
# - meta-llama/llama-3-3-70b-instruct (High quality)
# - ibm/granite-3-8b-instruct (Lightweight)

config["deep_think_llm"] = "mistralai/mixtral-8x7b-instruct-v01"
config["quick_think_llm"] = "ibm/granite-3-8b-instruct"  # Use lighter model
```

## Troubleshooting

### Error: langchain-ibm not installed

```bash
watsonx_env\Scripts\activate
uv pip install langchain-ibm ibm-watsonx-ai
```

### Error: Authentication failed

Verify your credentials:
```bash
echo %WATSONX_APIKEY%
echo %WATSONX_PROJECT_ID%
```

### Error: Model not found

Check available models in your WatsonX project:
1. Go to watsonx.ai
2. Navigate to your project
3. Check "Foundation models" section

Use `mistralai/mixtral-8x7b-instruct-v01` - it's most widely available.

### Analysis is slow

Reduce analysts:
```python
selected_analysts = ["market", "fundamentals"]  # Only 2 analysts
config["max_debate_rounds"] = 1  # Reduce debate depth
```

## Next Steps

1. **Review Output**: Check `results/NVDA/2025-10-10/` for generated reports
2. **Try Portfolio**: Set `portfolio_mode = True` for multi-stock analysis
3. **Customize**: Adjust analyst selection and parameters
4. **Automate**: Set up scheduled runs for daily analysis

## Support

- **Documentation**: See `WATSONX_SETUP.md` for detailed setup
- **Examples**: Check `main_enterprise_watsonx.py` for configuration options
- **Issues**: Review logs in `enterprise_watsonx_output.log`

## Security Note

⚠️ **IMPORTANT**: Your credentials are sensitive!

- Do NOT commit `.env.watsonx` or `set_watsonx_env.bat` to version control
- Do NOT share your API key publicly
- Consider using IBM Cloud IAM for production deployments
- Rotate keys regularly for security

Add to `.gitignore`:
```
.env.watsonx
set_watsonx_env.bat
*.log
```

---

**Ready to analyze?** Run: `python main_enterprise_watsonx.py`
