# Interactive Trading Analysis System

## 🎯 Overview

The **Interactive Trading Analysis System** extends the TradingAgents platform with **human-in-the-loop** capabilities, allowing you to actively guide and collaborate with AI analysts throughout the analysis process.

### Key Features

✅ **User Preference Injection** - Tell analysts what you care about before they start
✅ **Real-time Review** - See each analyst's work as they complete it
✅ **Feedback & Revision** - Request changes, clarifications, or expansions
✅ **Intelligent Parsing** - LLM understands your preferences and feedback
✅ **Beautiful Gradio UI** - Clean, multi-tab web interface
✅ **WatsonX Integration** - Full support for IBM WatsonX AI models

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Sync all dependencies (includes Gradio)
uv sync
```

### 2. Configure WatsonX

**Option A: Environment Variables**
```bash
export WATSONX_URL="https://us-south.ml.cloud.ibm.com"
export WATSONX_APIKEY="your-api-key"
export WATSONX_PROJECT_ID="your-project-id"
```

**Option B: Edit Config**
Open `main_interactive_watsonx.py` and update `WATSONX_CONFIG`.

### 3. Launch UI

**Windows:**
```bash
RUN_INTERACTIVE_UI.bat
```

**Mac/Linux:**
```bash
python main_interactive_watsonx.py
```

**Access the UI:** http://localhost:7860

---

## 📋 How It Works

### Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: User Input                                             │
│  ├─ Select stock ticker (e.g., NVDA)                            │
│  ├─ Choose analysts (Market, Fundamentals, News, etc.)          │
│  └─ Provide preferences (focus areas, principles, constraints)  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: LLM Parses Preferences                                 │
│  ├─ Extracts focus areas (e.g., "cash flow", "profitability")   │
│  ├─ Identifies principles (e.g., "conservative estimates")      │
│  ├─ Detects constraints (e.g., "avoid technical indicators")    │
│  └─ Determines risk tolerance & investment horizon              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Analyst Execution Loop (for each analyst)              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 3a. Inject Preferences into Analyst Prompt                │  │
│  │     └─ Custom instructions based on user's preferences    │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 3b. Run Analyst (via LangGraph node)                      │  │
│  │     └─ Analyst performs analysis with user context        │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 3c. Show Report to User                                   │  │
│  │     └─ Display full analysis in UI                        │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 3d. Collect User Feedback                                 │  │
│  │     ├─ Approve → Next analyst                             │  │
│  │     ├─ Request revision → Rerun with feedback             │  │
│  │     └─ Ask questions → Expand analysis                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 3e. If Revision Requested:                                │  │
│  │     ├─ LLM analyzes feedback                              │  │
│  │     ├─ Generates revision instructions                    │  │
│  │     └─ Re-executes analyst with new context              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Final Decision                                         │
│  ├─ Aggregate all approved analyst reports                      │
│  ├─ Generate comprehensive trading recommendation              │
│  └─ Display final decision with all context                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

### Module Structure

```
tradingagents/interactive/
├── user_preference_parser.py     # Parses natural language preferences
├── feedback_analyzer.py          # Analyzes user feedback on reports
├── interactive_workflow.py       # Orchestrates the workflow
├── graph_executor_helper.py      # Executes individual analyst nodes
├── gradio_ui.py                  # Gradio web interface
└── __init__.py                   # Module exports
```

### Key Components

#### 1. **User Preference Parser** (`user_preference_parser.py`)

**Purpose:** Convert natural language user input into structured preferences.

**Input Example:**
```
I'm a conservative long-term investor. Focus on profitability and cash flow.
Don't rely too much on technical indicators. Avoid speculative recommendations.
```

**Output:**
```python
UserPreferences(
    focus_areas=["profitability", "cash flow", "earnings stability"],
    principles=["conservative estimates", "long-term fundamentals"],
    constraints=["over-reliance on technical indicators", "speculative plays"],
    risk_tolerance="conservative",
    investment_horizon="long-term"
)
```

**How It Works:**
- Uses LLM (same model as analysis) to extract structured info
- Generates analyst-specific instructions
- Injects context into each analyst's system prompt

---

#### 2. **Feedback Analyzer** (`feedback_analyzer.py`)

**Purpose:** Interpret user feedback and determine appropriate actions.

**Feedback Types:**

| User Says | Action | What Happens |
|-----------|--------|--------------|
| "Looks good", "ok", "approved" | APPROVE | Move to next analyst |
| "I disagree with X" | REVISE | Re-analyze with corrections |
| "Tell me more about Y" | EXPAND | Add more details on Y |
| "Why did you say Z?" | CLARIFY | Answer questions |

**How It Works:**
- LLM analyzes feedback context
- Determines action type (approve/revise/expand/clarify)
- Extracts focus points and questions
- Generates revision instructions if needed

---

#### 3. **Interactive Workflow Controller** (`interactive_workflow.py`)

**Purpose:** Manage the overall interactive workflow with approval gates.

**State Management:**
```python
WorkflowState:
  - stage: (initialization → analysis → review → final)
  - current_analyst_index: Which analyst is running
  - analyst_statuses: Status of each analyst
  - user_preferences: Parsed preferences
  - agent_state: LangGraph state
```

**Key Methods:**
- `initialize()` - Set up analysis with preferences
- `run_current_analyst()` - Execute next analyst
- `process_feedback()` - Handle user feedback
- `get_final_decision()` - Generate final report

---

#### 4. **Graph Executor Helper** (`graph_executor_helper.py`)

**Purpose:** Execute individual LangGraph analyst nodes.

**Challenge:** LangGraph executes entire graphs, but we need single-node execution.

**Solution:**
- Directly calls analyst node creation functions
- Wraps analyst execution with preference injection
- Merges results back into shared state

**Key Methods:**
- `execute_analyst_node()` - Run specific analyst
- `create_initial_state()` - Initialize AgentState
- `merge_state_with_report()` - Update state with results

---

#### 5. **Gradio UI** (`gradio_ui.py`)

**Purpose:** Provide clean web interface for interaction.

**Three-Tab Design:**

**Tab 1: Setup & Preferences**
- Stock ticker input
- Analyst selection (checkboxes)
- Preference text area
- Start button

**Tab 2: Analysis & Review**
- Progress bar
- "Run Next Analyst" button
- Analyst report display
- Feedback input
- Approve/Revision buttons

**Tab 3: Final Decision**
- Comprehensive report
- Analysis history (JSON)
- Export options

---

## 💡 Usage Examples

### Example 1: Conservative Investor

**Setup:**
```
Ticker: JNJ (Johnson & Johnson)
Analysts: Fundamentals, News, Market
Preferences:
  I'm a conservative dividend investor focused on stability.
  Key priorities: dividend yield, payout ratio, and debt levels.
  I don't care about short-term price movements.
  Risk tolerance: very conservative. Horizon: 10+ years.
```

**Analysis Flow:**

1. **Fundamentals Analyst** runs → Reports P/E=15, Div Yield=2.8%, Debt/Equity=0.5
2. User reviews → "Great, but tell me more about dividend sustainability"
3. Analyst expands → Adds payout ratio analysis, 5-year dividend growth
4. User approves → Moves to News Analyst
5. **News Analyst** runs → Reports on recent pharma lawsuits
6. User reviews → "I'm concerned about legal risks. Re-analyze impact on cash flow"
7. Analyst revises → Detailed legal risk analysis with cash flow projections
8. User approves → Moves to Market Analyst
9. **Market Analyst** runs → Technical analysis
10. User approves immediately (less important for long-term)
11. **Final Decision** → HOLD recommendation with dividend focus

---

### Example 2: Growth Investor

**Setup:**
```
Ticker: NVDA
Analysts: Market, Fundamentals, Quantitative, News
Preferences:
  Bullish on AI long-term. Focus on GPU market share and data center revenue.
  Willing to accept volatility for growth potential.
  Risk tolerance: aggressive. Horizon: 2-3 years.
```

**Analysis Flow:**

1. **Market Analyst** → RSI, MACD, price targets
2. User: "What about the recent 20% correction?"
3. Analyst expands → Correction analysis, support levels
4. **Fundamentals** → Revenue growth, margins, competitive position
5. User: "Approved"
6. **Quantitative** → GARCH forecasts, ML predictions
7. User: "Your forecast seems too conservative. Re-run with higher growth assumptions"
8. Analyst revises → Updated forecasts
9. **News** → AI chip demand, new product launches
10. **Final** → BUY recommendation with $XXX target

---

## 🔧 Configuration

### WatsonX Models

Edit `main_interactive_watsonx.py`:

```python
WATSONX_CONFIG = {
    "llm_provider": "watsonx",

    # Model Selection
    "deep_think_llm": "mistralai/mixtral-8x7b-instruct-v01",  # Best for tool calling
    # Alternatives:
    # "meta-llama/llama-3-3-70b-instruct"  # Granite 3.0
    # "ibm/granite-3-8b-instruct"  # Lightweight

    "quick_think_llm": "mistralai/mixtral-8x7b-instruct-v01",

    # Analysis Settings
    "max_debate_rounds": 2,
    "enterprise_mode": True,
    "online_tools": True,  # Real-time data vs cached
}
```

### UI Customization

**Change Port:**
```python
launch_ui(config=WATSONX_CONFIG, server_port=8080)
```

**Enable Public Sharing:**
```python
launch_ui(config=WATSONX_CONFIG, share=True)  # Creates public URL
```

---

## 📊 State Management

### AgentState Extensions

The interactive system extends `AgentState` with:

```python
class AgentState(MessagesState):
    # ... existing fields ...

    # NEW: User preferences (interactive mode)
    user_preferences: Optional[dict]

    # NEW: Enterprise strategy report
    enterprise_strategy_report: str
```

### Workflow State

```python
@dataclass
class WorkflowState:
    stage: WorkflowStage  # Current workflow stage
    company_of_interest: str
    trade_date: str
    selected_analysts: List[str]
    user_preferences: UserPreferences

    # Per-analyst tracking
    analyst_statuses: Dict[str, AnalystStatus]
    current_analyst_index: int

    # Shared state
    agent_state: AgentState
```

---

## 🧪 Testing

### Manual Testing

```bash
# 1. Launch UI
python main_interactive_watsonx.py

# 2. In browser:
#    - Enter ticker: NVDA
#    - Select: Market, Fundamentals
#    - Preferences: "Focus on profitability. Conservative approach."
#    - Click Start
#    - Run analysts one by one
#    - Provide feedback
#    - Generate final decision
```

### Automated Testing

```bash
# Run unit tests (TODO: Add test suite)
pytest tests/interactive/
```

---

## 📝 Development Guide

### Adding a New Analyst

1. **Create analyst in `tradingagents/agents/analysts/`**
2. **Add node to `graph/setup.py`**
3. **Update `ANALYST_REPORT_FIELDS` in `graph_executor_helper.py`**:
   ```python
   ANALYST_REPORT_FIELDS = {
       # ...
       "my_new_analyst": "my_new_analyst_report",
   }
   ```
4. **Add mapping in `gradio_ui.py`**:
   ```python
   AVAILABLE_ANALYSTS = {
       # ...
       "my_new_analyst": "🔍 My New Analyst (Description)",
   }
   ```
5. **Update `AgentState` in `agent_states.py`**:
   ```python
   my_new_analyst_report: Annotated[str, "Report from My New Analyst"]
   ```

### Customizing Preference Parsing

Edit the `SYSTEM_PROMPT` in `user_preference_parser.py` to extract additional fields:

```python
SYSTEM_PROMPT = """
...
Extract these fields:
- focus_areas
- principles
- constraints
- risk_tolerance
- investment_horizon
- custom_field_1  # NEW
- custom_field_2  # NEW
...
"""
```

### Customizing Feedback Analysis

Edit `SYSTEM_PROMPT` in `feedback_analyzer.py` to add new action types:

```python
class FeedbackAction(Enum):
    APPROVE = "approve"
    REVISE = "revise"
    EXPAND = "expand"
    CLARIFY = "clarify"
    DEEP_DIVE = "deep_dive"  # NEW custom action
```

---

## 🐛 Troubleshooting

### UI Won't Launch

**Error:** `ModuleNotFoundError: No module named 'gradio'`

**Solution:**
```bash
uv sync
# or
pip install gradio>=5.0.0
```

---

**Error:** `Missing required WatsonX configuration`

**Solution:**
```bash
export WATSONX_APIKEY="your-key"
export WATSONX_PROJECT_ID="your-id"
```

---

### Analyst Execution Fails

**Error:** `Error executing market analyst: ...`

**Check:**
1. Is the analyst type spelled correctly?
2. Does the analyst exist in `graph/setup.py`?
3. Check `enterprise_output.log` for details

**Debug:**
```python
# In gradio_ui.py, enable verbose logging
WATSONX_CONFIG["verbose"] = True
```

---

### Feedback Not Working

**Issue:** Feedback is misinterpreted

**Solution:** Be more explicit:
- ❌ "Not good" → Ambiguous
- ✅ "Re-analyze focusing on debt levels" → Clear

**Issue:** Revision loop doesn't update

**Check:** Ensure `revision_count` is incrementing in `AnalystStatus`

---

### UI Freezes

**Issue:** Long-running analyst blocks UI

**Solution:** Add progress indicators (future enhancement)

**Workaround:** Use fewer analysts or lightweight mode:
```python
"lightweight_quantitative": True
```

---

## 🚀 Roadmap

### Planned Features

- [ ] **Save/Load Sessions** - Resume analysis later
- [ ] **Preference Profiles** - Save reusable preference templates
- [ ] **Side-by-Side Comparison** - Compare multiple stocks
- [ ] **Chart Integration** - Show charts in analyst reports
- [ ] **Export to PDF** - Professional report export
- [ ] **Voice Input** - Speak your preferences
- [ ] **Real-time Streaming** - See analyst thinking in real-time
- [ ] **Collaborative Mode** - Multiple users review together
- [ ] **Backtesting Integration** - Test decisions against history

---

## 📚 API Reference

### UserPreferences

```python
@dataclass
class UserPreferences:
    focus_areas: List[str]         # Metrics/indicators to emphasize
    principles: List[str]          # Analytical methodologies
    constraints: List[str]         # Things to avoid
    risk_tolerance: str            # conservative|moderate|aggressive
    investment_horizon: str        # short-term|medium-term|long-term
    custom_instructions: str       # Freeform instructions
    raw_input: str                 # Original user input

    def to_prompt_context(self) -> str:
        """Convert to formatted text for prompt injection"""
```

### FeedbackAnalysis

```python
@dataclass
class FeedbackAnalysis:
    action: FeedbackAction          # approve|revise|expand|clarify
    focus_points: List[str]         # Specific aspects mentioned
    questions: List[str]            # User's questions
    revision_instructions: str      # Instructions for re-analysis
    confidence: float               # 0-1 confidence score
    raw_feedback: str               # Original feedback

    def needs_revision(self) -> bool:
        """Check if revision is needed"""
```

### InteractiveWorkflowController

```python
class InteractiveWorkflowController:
    def initialize(
        self,
        company_of_interest: str,
        trade_date: str,
        selected_analysts: List[str],
        user_preference_text: str
    ):
        """Initialize the workflow"""

    def run_current_analyst(self) -> Dict[str, Any]:
        """Run the next analyst in sequence"""

    def process_feedback(self, feedback_text: str) -> FeedbackAnalysis:
        """Process user feedback on current analyst"""

    def get_final_decision(self) -> str:
        """Generate final trading decision"""

    def get_state_summary(self) -> Dict[str, Any]:
        """Get current workflow state"""
```

---

## 💬 Support

For questions or issues:

1. Check `enterprise_output.log` for detailed logs
2. Review analyst logs in `eval_results/TICKER/`
3. Read full user guide: `INTERACTIVE_USAGE.md`
4. Open an issue on GitHub

---

## 🎓 Best Practices

### 1. **Be Specific in Preferences**

❌ **Vague:** "I want good stocks"
✅ **Specific:** "Focus on ROE > 15%, dividend yield > 2%, and stable earnings growth"

### 2. **Iterate on Feedback**

Don't approve immediately. Use the revision loop to refine analysis:
- First pass: General analysis
- Second pass: Deep dive on specific concerns
- Third pass: Clarify remaining questions

### 3. **Balance Analyst Selection**

Mix different perspectives:
- **Technical** (Market) + **Fundamental** = Complete picture
- **Quantitative** + **News** = Data + Context

### 4. **Review Before Approving**

Actually read the reports. The system is designed for human oversight, not automation.

### 5. **Save Important Sessions**

Copy the Analysis History JSON for your records.

---

## 🔒 Security Notes

- **API Keys:** Never commit WatsonX credentials to git
- **Data Privacy:** All analysis stays local (no external data sharing)
- **UI Access:** By default, UI is only accessible on localhost
- **Public Sharing:** Only enable `share=True` in trusted environments

---

## 📄 License

Same as TradingAgents main project.

---

**Built with ❤️ for traders who want AI collaboration, not AI replacement.**
