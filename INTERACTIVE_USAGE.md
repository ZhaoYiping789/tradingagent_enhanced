# Interactive Trading Analysis System - User Guide

## Overview

The Interactive Trading Analysis System provides a **human-in-the-loop** workflow that allows you to:

1. **Guide the analysis** with your own preferences, principles, and constraints
2. **Review each analyst's work** in real-time as they complete their analysis
3. **Provide feedback** to refine and improve analyst reports
4. **Approve or request revisions** before moving to the next analyst
5. **Get a comprehensive final decision** based on all analysts' insights

This creates a collaborative experience where AI analysts work **with you**, not just for you.

## Quick Start

### 1. Install Dependencies

```bash
# Install Gradio and WatsonX AI SDK
uv sync
```

### 2. Set WatsonX Credentials

**Option A: Environment Variables (Recommended)**
```bash
export WATSONX_URL="https://us-south.ml.cloud.ibm.com"
export WATSONX_APIKEY="your-api-key"
export WATSONX_PROJECT_ID="your-project-id"
```

**Option B: Edit the Configuration File**
Edit `main_interactive_watsonx.py` and update the `WATSONX_CONFIG` dictionary.

**Option C: Use the Batch File (Windows)**
Edit `RUN_INTERACTIVE_UI.bat` and set your credentials there.

### 3. Launch the UI

**Windows:**
```bash
RUN_INTERACTIVE_UI.bat
```

**Mac/Linux:**
```bash
python main_interactive_watsonx.py
```

The UI will open in your browser at **http://localhost:7860**

## Using the Interactive UI

### Step 1: Setup & Preferences

#### Basic Configuration

1. **Stock Ticker**: Enter the stock symbol (e.g., `NVDA`, `AAPL`, `MSFT`)
2. **Analysis Date**: Specify the date or leave blank for today
3. **Select Analysts**: Choose which analysts you want to run:
   - 📊 **Market/Technical Analyst** - Charts, indicators, price patterns
   - 💰 **Fundamentals Analyst** - Financial statements, ratios, profitability
   - 📰 **News Analyst** - Recent news sentiment and impact
   - 🗣️ **Social Media Analyst** - Reddit/Twitter sentiment
   - 🔬 **Quantitative Analyst** - ML forecasting, GARCH models
   - 📈 **Portfolio Analyst** - Correlation, diversification
   - 🏢 **Enterprise Strategy Analyst** - Institutional-level strategy

#### Your Analysis Preferences (Optional but Powerful!)

This is where you **guide** the analysis. In the preferences box, you can specify:

**Focus Areas** - What metrics/aspects matter most to you:
```
I care most about profitability, cash flow, and debt levels.
Pay special attention to operating margins and free cash flow.
```

**Principles** - How you want the analysis conducted:
```
Use conservative estimates. Focus on long-term fundamentals rather than short-term price movements.
Don't over-rely on technical indicators alone.
```

**Constraints** - Things to avoid or be cautious about:
```
Avoid speculative recommendations. I don't trust social media sentiment for investment decisions.
No leverage or derivatives recommendations.
```

**Risk Tolerance & Horizon**:
```
I'm risk-averse and investing for the long term (5+ years).
```

**Example Complete Preference Input:**
```
I'm a conservative long-term investor focused on dividend-paying stocks.
Key priorities: profitability, cash flow stability, and competitive moat.
Don't care much about short-term price volatility or technical patterns.
Avoid speculative growth plays. I prefer established companies with proven track records.
Risk tolerance: conservative. Investment horizon: 5-10 years.
```

The system will **parse your preferences** and inject them into each analyst's instructions!

Click **🚀 Start Analysis** when ready.

### Step 2: Analysis & Review

#### Real-Time Analysis

1. Click **▶️ Run Next Analyst** to execute the next analyst
2. Watch as the analyst performs their analysis
3. Review the detailed report when complete

#### Review & Feedback

After each analyst completes, you'll see:
- The analyst's full report
- Duration of the analysis
- A feedback input box

**You have three options:**

**Option 1: Approve and Continue**
```
Type: "ok", "approved", "looks good", or just "yes"
Result: Moves to the next analyst
```

**Option 2: Request More Details**
```
Type: "Can you explain the P/E ratio calculation in more detail?"
      "Tell me more about the competitive landscape"
Result: Analyst expands on specific topics
```

**Option 3: Request Revision**
```
Type: "I don't think you considered the recent acquisition impact"
      "Re-analyze with more focus on cash flow, less on revenue growth"
Result: Analyst revises the analysis with your feedback
```

The system uses **LLM-powered feedback analysis** to understand your intent and generate appropriate follow-up instructions for the analyst.

#### Progress Tracking

- **Progress Bar**: Shows overall completion percentage
- **Analyst Status**: Shows which analyst is currently running
- **Analysis History**: Tracks all completed analyses

### Step 3: Final Decision

Once all analysts have completed and been approved:

1. Go to the **3️⃣ Final Decision** tab
2. Click **📊 Generate Final Decision**
3. Review the comprehensive trading recommendation

The final decision synthesizes:
- All analyst reports
- Your original preferences
- Any revisions made based on your feedback

### Step 4: Download & Export

The analysis history section shows all analyst reports in JSON format, which you can:
- Download for your records
- Import into other tools
- Share with colleagues

## Advanced Features

### Multi-Revision Workflow

You can request multiple revisions from the same analyst:

1. Analyst completes initial analysis
2. You provide feedback → Analyst revises
3. Review revision
4. Provide more feedback → Analyst revises again
5. Finally approve

Each revision builds on the previous version.

### Dynamic Preference Injection

Your preferences are **dynamically injected** into each analyst's system prompt:

- **Market Analyst** gets guidance on which technical indicators to emphasize
- **Fundamentals Analyst** knows which financial metrics you prioritize
- **News Analyst** understands what news themes matter to you
- All analysts respect your risk tolerance and investment horizon

### Feedback Intelligence

The system intelligently interprets your feedback:

| You Say | System Understands |
|---------|-------------------|
| "Looks good" | APPROVE → Next analyst |
| "What about competition?" | CLARIFY → Answer questions |
| "I disagree with the valuation" | REVISE → Re-analyze valuation |
| "Tell me more about cash flow" | EXPAND → Add more details |

## Configuration Options

### Changing LLM Models

Edit `main_interactive_watsonx.py`:

```python
WATSONX_CONFIG = {
    "deep_think_llm": "mistralai/mixtral-8x7b-instruct-v01",  # Complex reasoning
    "quick_think_llm": "mistralai/mixtral-8x7b-instruct-v01",  # Fast operations
}
```

**Recommended models:**
- `mistralai/mixtral-8x7b-instruct-v01` (best tool calling)
- `meta-llama/llama-3-3-70b-instruct` (Granite 3.0, high quality)
- `ibm/granite-3-8b-instruct` (lightweight, faster)

### Enabling Offline Mode

To use cached data instead of live API calls:

```python
WATSONX_CONFIG = {
    "online_tools": False,  # Use cached data
}
```

### Sharing the UI

To create a public link (e.g., share with team members):

Edit `main_interactive_watsonx.py`:
```python
launch_ui(
    config=WATSONX_CONFIG,
    share=True,  # Creates public URL
)
```

## Tips for Best Results

### 1. Be Specific in Preferences

❌ Bad: "I want good stocks"
✅ Good: "I prioritize companies with ROE > 15%, dividend yield > 2%, and debt-to-equity < 0.5"

### 2. Use Feedback to Iterate

Don't settle for the first analysis. If something seems off, ask for revision:
- "Re-analyze this considering the recent CEO change"
- "I think you missed the regulatory risks in Europe"

### 3. Balance Analysts

Don't just pick one analyst type. A balanced selection gives you:
- Technical + Fundamental = Complete picture
- News + Social = Sentiment context
- Quantitative = Data-driven forecasts

### 4. Review Before Approving

Actually **read** each analyst's report before clicking "approved". The system is designed for thoughtful human oversight, not rubber-stamping.

### 5. Save Your Work

The Analysis History tab contains all reports. **Copy the JSON** to save your complete analysis session.

## Troubleshooting

### UI Won't Start

**Check WatsonX credentials:**
```bash
echo $WATSONX_APIKEY
echo $WATSONX_PROJECT_ID
```

**Reinstall dependencies:**
```bash
uv sync --reinstall
```

### Analyst Takes Too Long

**Use lightweight mode:**
```python
"lightweight_quantitative": True,  # Faster quantitative analysis
"max_debate_rounds": 1,  # Fewer debate rounds
```

**Or select fewer analysts** in the UI.

### Feedback Not Working

Make sure you click **✅ Submit Feedback** after typing your feedback.

If the system misinterprets your feedback, be more explicit:
- Instead of "not good", say "revise this focusing on debt levels"

### Analysis Errors

Check the console/terminal where you launched the UI for detailed error messages.

Common issues:
- **API key invalid** → Check WatsonX credentials
- **Ticker not found** → Use valid stock symbols
- **Date too old** → Some data sources have limited history

## Architecture

The interactive system consists of:

1. **User Preference Parser** (`user_preference_parser.py`)
   - Uses LLM to extract structured preferences from natural language
   - Generates analyst-specific instructions

2. **Feedback Analyzer** (`feedback_analyzer.py`)
   - Interprets user feedback (approve/revise/expand/clarify)
   - Generates revision prompts for analysts

3. **Interactive Workflow Controller** (`interactive_workflow.py`)
   - Manages analyst execution sequence
   - Handles approval gates and revision loops
   - Tracks analysis state

4. **Gradio UI** (`gradio_ui.py`)
   - Web interface with three-tab workflow
   - Real-time progress tracking
   - Feedback collection and display

## Example Session

**Scenario**: Analyzing NVDA with focus on AI growth

### Setup Phase
```
Ticker: NVDA
Analysts: Market, Fundamentals, News, Quantitative
Preferences:
  "I'm bullish on AI long-term. Focus on GPU market share,
   data center revenue growth, and competitive positioning
   vs AMD/Intel. Risk tolerance: moderate-aggressive.
   Investment horizon: 2-3 years."
```

### Analysis Phase

**Market Analyst** completes:
- Shows RSI, MACD, price targets
- You ask: "What about the recent price correction? Is it a buying opportunity?"
- Analyst expands with correction analysis
- You approve

**Fundamentals Analyst** completes:
- Shows revenue growth, margins, P/E ratio
- You say: "Focus more on data center segment breakdown"
- Analyst revises with detailed segment analysis
- You approve

**News Analyst** completes:
- Reports on recent AI chip news
- You approve immediately (looks good)

**Quantitative Analyst** completes:
- GARCH forecasts, price predictions
- You approve

### Final Decision Phase

System generates comprehensive recommendation:
- BUY recommendation
- Price target: $XXX
- Risk assessment: Moderate
- Based on all 4 analysts + your preferences

## Support & Feedback

For issues or suggestions:
1. Check `enterprise_output.log` for detailed logs
2. Review analyst-specific logs in `eval_results/`
3. Open an issue on the project repository

## What's Next?

Future enhancements planned:
- [ ] Save/load preference profiles
- [ ] Compare multiple stocks side-by-side
- [ ] Export to PDF with charts
- [ ] Voice input for preferences
- [ ] Real-time portfolio tracking
- [ ] Backtesting integration

---

**Happy analyzing! Let the AI analysts work for you, with your guidance.** 🚀
