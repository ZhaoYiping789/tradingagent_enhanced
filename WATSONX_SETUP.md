# IBM WatsonX Integration Setup Guide

This guide provides step-by-step instructions for setting up TradingAgents with IBM WatsonX.ai LLM integration.

## Prerequisites

- Python 3.10 or higher
- UV package manager (recommended) or pip
- IBM Cloud account with WatsonX.ai access
- WatsonX project with appropriate models deployed

## Quick Start

### 1. Setup WatsonX Environment

```bash
# For Windows
setup_watsonx_env.bat

# For Linux/Mac
bash setup_watsonx_env.sh
```

Or manually with UV:

```bash
# Create isolated WatsonX environment
uv venv watsonx_env

# Activate environment
# Windows:
watsonx_env\Scripts\activate
# Linux/Mac:
source watsonx_env/bin/activate

# Install dependencies
uv pip install langchain-ibm ibm-watsonx-ai
uv sync
```

### 2. Get WatsonX Credentials

#### Step 2.1: Get API Key

1. Go to [IBM Cloud API Keys](https://cloud.ibm.com/iam/apikeys)
2. Click "Create +"
3. Name your key (e.g., "TradingAgents")
4. Click "Create"
5. **IMPORTANT**: Copy and save the API key immediately (it won't be shown again)

#### Step 2.2: Get Project ID

1. Go to [WatsonX.ai](https://dataplatform.cloud.ibm.com/wx/home)
2. Navigate to "Projects"
3. Select or create your project
4. Go to "Manage" tab > "General"
5. Copy the "Project ID"

### 3. Configure Environment Variables

```bash
# Windows
set WATSONX_API_KEY=your_api_key_here
set WATSONX_PROJECT_ID=your_project_id_here
set WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Linux/Mac
export WATSONX_API_KEY="your_api_key_here"
export WATSONX_PROJECT_ID="your_project_id_here"
export WATSONX_URL="https://us-south.ml.cloud.ibm.com"
```

Or create a `.env` file:

```bash
# Copy the example configuration
cp config_watsonx_example.env .env

# Edit .env with your credentials
# Then load it:
source .env  # Linux/Mac
# or use python-dotenv in your script
```

### 4. Run Analysis

```bash
# Single stock analysis with WatsonX
uv run main_enterprise_watsonx.py

# Or activate environment first
watsonx_env\Scripts\activate  # Windows
source watsonx_env/bin/activate  # Linux/Mac
python main_enterprise_watsonx.py
```

## Supported Models

### Recommended Models (with Function Calling)

| Model ID | Description | Best For |
|----------|-------------|----------|
| `mistralai/mixtral-8x7b-instruct-v01` | Mistral Mixtral 8x7B | **Best tool calling support** |
| `meta-llama/llama-3-3-70b-instruct` | IBM Granite 3.0 (70B) | High-quality reasoning |
| `ibm/granite-3-8b-instruct` | IBM Granite 3.0 (8B) | Balanced performance |
| `ibm/granite-3-2b-instruct` | IBM Granite 3.0 (2B) | Lightweight/fast |

### Configuration in Code

Edit `main_enterprise_watsonx.py`:

```python
config["deep_think_llm"] = "mistralai/mixtral-8x7b-instruct-v01"
config["quick_think_llm"] = "mistralai/mixtral-8x7b-instruct-v01"
```

## Advanced Configuration

### Custom Generation Parameters

```python
config = {
    "llm_provider": "watsonx",
    "deep_think_llm": "mistralai/mixtral-8x7b-instruct-v01",
    "quick_think_llm": "mistralai/mixtral-8x7b-instruct-v01",

    # Generation parameters
    "max_tokens": 4096,
    "temperature": 0.7,
    "top_p": 1.0,

    # WatsonX specific
    "watsonx_url": "https://us-south.ml.cloud.ibm.com",
    "watsonx_project_id": "your_project_id",
    "watsonx_api_key": "your_api_key",
}
```

### Region Selection

Available WatsonX regions:

- **US South**: `https://us-south.ml.cloud.ibm.com` (default)
- **Frankfurt**: `https://eu-de.ml.cloud.ibm.com`
- **London**: `https://eu-gb.ml.cloud.ibm.com`
- **Tokyo**: `https://jp-tok.ml.cloud.ibm.com`

Choose the region closest to you for best performance.

## Feature Compatibility

### ✅ Fully Supported

- Single stock analysis
- Portfolio analysis (multiple stocks)
- All analyst types (market, fundamentals, news, social, quantitative)
- Investment committee debates (bull/bear researchers)
- Risk assessment debates
- Report generation (Markdown, Word, CSV)
- Chart generation
- Multi-scenario portfolio optimization
- Tool calling / function calling

### 🚧 Model-Specific Limitations

- **Tool Calling**: Currently best supported with `mistralai/mixtral-8x7b-instruct-v01`
- **Other Models**: May work but have limited function calling capabilities
- Refer to IBM documentation for latest model capabilities

## Troubleshooting

### Issue: Import Error - langchain-ibm not found

```bash
# Ensure you're in the WatsonX environment
watsonx_env\Scripts\activate  # Windows
source watsonx_env/bin/activate  # Linux/Mac

# Reinstall dependencies
uv pip install langchain-ibm ibm-watsonx-ai
```

### Issue: Authentication Failed

- Verify API key is correct and active
- Check project ID matches your WatsonX project
- Ensure your IBM Cloud account has WatsonX access
- Verify API key has appropriate permissions

### Issue: Model Not Found

- Check model is available in your WatsonX region
- Verify model is deployed in your project
- Try using `mistralai/mixtral-8x7b-instruct-v01` (most widely available)

### Issue: Tool Calling Not Working

- Use `mistralai/mixtral-8x7b-instruct-v01` model (best tool calling support)
- Check model version is up to date
- Verify `bind_tools()` is being called in analyst code

### Issue: Rate Limit Errors

- Monitor your usage in IBM Cloud dashboard
- Reduce `max_debate_rounds` and `max_risk_discuss_rounds`
- Use lighter models for `quick_think_llm`
- Add delays between API calls

## Performance Tips

### 1. Cost Optimization

```python
# Use lighter model for quick operations
config["deep_think_llm"] = "mistralai/mixtral-8x7b-instruct-v01"
config["quick_think_llm"] = "ibm/granite-3-8b-instruct"  # Lighter

# Reduce debate rounds
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1
```

### 2. Speed Optimization

```python
# Use lightweight quantitative mode
config["lightweight_quantitative"] = True

# Select fewer analysts
selected_analysts = ["market", "fundamentals"]  # Minimal set
```

### 3. Quality Optimization

```python
# Use best models
config["deep_think_llm"] = "meta-llama/llama-3-3-70b-instruct"
config["quick_think_llm"] = "mistralai/mixtral-8x7b-instruct-v01"

# Increase debate depth
config["max_debate_rounds"] = 3
config["max_risk_discuss_rounds"] = 3
```

## Migration from OpenAI

If you're migrating from OpenAI to WatsonX:

### 1. Update Configuration

**Before (OpenAI)**:
```python
config["llm_provider"] = "openai"
config["deep_think_llm"] = "gpt-4o"
config["quick_think_llm"] = "gpt-4o-mini"
```

**After (WatsonX)**:
```python
config["llm_provider"] = "watsonx"
config["deep_think_llm"] = "mistralai/mixtral-8x7b-instruct-v01"
config["quick_think_llm"] = "mistralai/mixtral-8x7b-instruct-v01"
```

### 2. Update Environment Variables

Remove:
```bash
OPENAI_API_KEY
```

Add:
```bash
WATSONX_API_KEY
WATSONX_PROJECT_ID
WATSONX_URL
```

### 3. Use WatsonX Script

Instead of:
```bash
python main_enterprise.py
```

Use:
```bash
python main_enterprise_watsonx.py
```

## Additional Resources

- [WatsonX.ai Documentation](https://www.ibm.com/docs/en/watsonx-as-a-service)
- [langchain-ibm GitHub](https://github.com/langchain-ai/langchain)
- [WatsonX Model Library](https://www.ibm.com/products/watsonx-ai/foundation-models)
- [IBM Cloud Console](https://cloud.ibm.com)

## Support

For issues specific to:
- **TradingAgents**: Create an issue in this repository
- **WatsonX.ai**: Contact IBM Cloud Support
- **langchain-ibm**: Check [LangChain documentation](https://python.langchain.com/docs/integrations/chat/ibm_watsonx/)
