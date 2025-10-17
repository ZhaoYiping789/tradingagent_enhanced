"""
Flask Chat Interface for Trading Analysis

Simple web chat interface without Gradio dependency.
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime
import json
import re
import pandas as pd
import yfinance as yf

# Fix Windows encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, errors="replace")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.interactive.interactive_workflow import InteractiveWorkflowController
from tradingagents.interactive.user_preference_parser import create_preference_parser
from tradingagents.interactive.feedback_analyzer import create_feedback_analyzer, FeedbackAction
from tradingagents.agents.utils.report_generator import generate_comprehensive_word_report

# WatsonX Configuration
WATSONX_CONFIG = {
    "llm_provider": "watsonx",
    "watsonx_url": os.getenv("WATSONX_URL") or "https://us-south.ml.cloud.ibm.com",
    "watsonx_api_key": os.getenv("WATSONX_APIKEY") or os.getenv("WATSONX_API_KEY") or "1NlP-L5h1DDEZFKkvJ92uTuMFNbkk0pmGJ4lMutJ44w2",
    "watsonx_project_id": os.getenv("WATSONX_PROJECT_ID") or "394811a9-3e1c-4b80-8031-3fda71e6dce1",
    "deep_think_llm": "meta-llama/llama-3-3-70b-instruct",
    "quick_think_llm": "meta-llama/llama-3-3-70b-instruct",
    "max_tokens": 32768,  # Maximum output tokens for comprehensive analysis (allows 12-15 news items with detailed analysis)
    "max_debate_rounds": 2,
    "enterprise_mode": True,
    "online_tools": True,  # CHANGED: Use online data instead of cached files
    "project_dir": str(project_root),
    "verbose": True,
}

app = Flask(__name__)

# Global state
graph = None
controller = None
waiting_for = None  # 'analyst_selection', 'initial_setup', 'feedback', 'optimization_preference', 'final_decision', 'next_stock_prompt', None
current_analyst = None
selected_analysts_choice = None  # User's chosen analysts
pending_ticker = None  # Store ticker while waiting for optimization preference
pending_analysts = None  # Store selected analysts while waiting for optimization preference
pending_user_message = None  # Store initial message while waiting for optimization preference

# Portfolio mode state
portfolio_mode = False
portfolio_tickers = []  # List of tickers to analyze
current_portfolio_ticker_index = 0  # Current ticker being analyzed
portfolio_results = {}  # Store results for each stock: {ticker: {state, report, decision}}
portfolio_trade_date = None  # Shared trade date for all stocks in portfolio
portfolio_optimization_preference = None  # Store optimization preference from first stock


def initialize_components():
    """Initialize graph and workflow controller"""
    global graph, controller

    if not graph:
        print("[INIT] Creating TradingAgentsGraph...", flush=True)
        graph = TradingAgentsGraph(
            selected_analysts=["market", "fundamentals", "news", "social", "quantitative", "comprehensive_quantitative", "visualizer"],  # Include ALL available analysts
            debug=False,
            config=WATSONX_CONFIG
        )

        llm = graph.quick_thinking_llm

        print("[INIT] Creating parsers...", flush=True)
        preference_parser = create_preference_parser(llm)
        feedback_analyzer = create_feedback_analyzer(llm)

        print("[INIT] Creating workflow controller...", flush=True)
        controller = InteractiveWorkflowController(
            graph=graph,
            preference_parser=preference_parser,
            feedback_analyzer=feedback_analyzer,
            ui_callback=None
        )
        print("[INIT] Initialization complete!", flush=True)


@app.route('/')
def index():
    """Serve the chat interface"""
    return send_from_directory('static', 'chat.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    global waiting_for, current_analyst

    try:
        data = request.json
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'error': 'Empty message'}), 400

        # If no state is set, initialize and show welcome
        if waiting_for is None:
            return welcome()

        # Handle analyst selection
        if waiting_for == 'analyst_selection':
            return handle_analyst_selection(message)

        # Handle initial setup
        if waiting_for == 'initial_setup':
            return handle_initial_setup(message)

        # Handle feedback
        if waiting_for == 'feedback':
            return handle_feedback(message)

        # Handle optimization preference
        if waiting_for == 'optimization_preference':
            return handle_optimization_preference(message)

        # Handle final decision request
        if waiting_for == 'final_decision':
            return handle_final_decision_request(message)

        # Handle next stock prompt (portfolio mode)
        if waiting_for == 'next_stock_prompt':
            return handle_next_stock_prompt(message)

        return jsonify({'error': 'Invalid state'}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/welcome', methods=['GET'])
def welcome():
    """Get initial welcome message"""
    global waiting_for
    waiting_for = 'analyst_selection'
    return jsonify({
        'response': """Welcome to AI Trading Analysis!

I'll help you analyze stocks using specialized AI analysts.

**First, please choose which analysts to use:**

- **market** - Technical/Market analysis (RSI, MACD, Bollinger Bands)
- **fundamentals** - Financial analysis (P/E, revenue, cash flow)
- **news** - News sentiment and impact
- **social** - Social media sentiment (Reddit, Twitter)
- **quantitative** - Quantitative analysis with ML forecasting (GARCH, statistical models)
- **comprehensive_quantitative** - Multi-scenario optimization (Kelly Criterion, risk optimization)
- **visualizer** - Interactive chart generation and visualization
- **all** - Use all analysts

Example: "market and fundamentals" or "all"

**Note:** You can analyze multiple stocks for portfolio optimization (e.g., "NVDA, AAPL")
""",
        'waiting_for': 'analyst_selection'
    })


def handle_analyst_selection(message):
    """Handle analyst selection"""
    global waiting_for, selected_analysts_choice

    # Parse analyst selection from user message
    message_lower = message.lower()
    analysts = []

    if 'all' in message_lower:
        analysts = ["market", "fundamentals", "news", "social", "quantitative", "comprehensive_quantitative", "visualizer"]
    else:
        if 'market' in message_lower or 'technical' in message_lower:
            analysts.append("market")
        if 'fundamental' in message_lower or 'financial' in message_lower:
            analysts.append("fundamentals")
        if 'news' in message_lower:
            analysts.append("news")
        if 'social' in message_lower or 'sentiment' in message_lower:
            analysts.append("social")
        # Check comprehensive_quantitative FIRST (with fuzzy matching for typos)
        if ('comprehensive' in message_lower and 'quant' in message_lower) or 'multi-scenario' in message_lower or 'multi scenario' in message_lower or 'optimization' in message_lower or 'optimizer' in message_lower or 'kelly' in message_lower:
            analysts.append("comprehensive_quantitative")
        elif 'quantitative' in message_lower or 'quant' in message_lower or 'ml' in message_lower or 'garch' in message_lower:
            analysts.append("quantitative")
        if 'visualizer' in message_lower or 'visual' in message_lower or 'chart' in message_lower:
            analysts.append("visualizer")

    if not analysts:
        return jsonify({
            'response': """Please choose which analysts to use. Type one or more:

- **market** - Technical/Market analysis (RSI, MACD, Bollinger Bands)
- **fundamentals** - Financial analysis (P/E, revenue, cash flow)
- **news** - News sentiment and impact
- **social** - Social media sentiment (Reddit, Twitter)
- **all** - Use all analysts

Example: "market and fundamentals" or "all"
""",
            'waiting_for': 'analyst_selection'
        })

    selected_analysts_choice = analysts
    waiting_for = 'initial_setup'

    analyst_names = {
        "market": "Market/Technical",
        "fundamentals": "Fundamentals",
        "news": "News",
        "social": "Social Media",
        "quantitative": "Quantitative (ML/GARCH)",
        "comprehensive_quantitative": "Multi-Scenario Optimizer",
        "visualizer": "Visualizer"
    }
    selected_names = [analyst_names[a] for a in analysts]

    return jsonify({
        'response': f"""Selected analysts: **{', '.join(selected_names)}**

Now, please provide:
1. **Stock ticker** (e.g., NVDA, AAPL)
2. **Your preferences** (optional - e.g., "I'm risk-averse, focus on fundamentals")

Example: "Analyze NVDA. I care about long-term growth and profitability."
""",
        'waiting_for': 'initial_setup'
    })


def handle_initial_setup(message):
    """Handle initial setup"""
    global waiting_for, current_analyst, selected_analysts_choice, pending_ticker, pending_analysts, pending_user_message

    try:
        # Check if user is correcting analyst selection
        # ONLY check correction keywords that are UNAMBIGUOUS (don't match optimization preferences)
        message_lower = message.lower()
        correction_keywords = ['i said', 'wrong', 'not', 'actually', 'meant', 'should be']
        is_correcting = any(keyword in message_lower for keyword in correction_keywords)

        # Also check if message contains analyst names but no stock ticker pattern
        # BUT EXCLUDE if message looks like optimization/preference description
        has_analyst_names = any(analyst in message_lower for analyst in ['market', 'fundamental', 'news', 'social', 'quantitative', 'visualizer'])
        has_stock_ticker = bool(re.search(r'\b([A-Z]{2,5})\b', message))
        looks_like_preference = any(word in message_lower for word in ['prefer', 'risk', 'balanced', 'aggressive', 'conservative', 'parity', 'variance', 'sharpe'])

        if is_correcting or (has_analyst_names and not has_stock_ticker and not looks_like_preference):
            # User is correcting analyst selection, go back to analyst_selection state
            waiting_for = 'analyst_selection'
            return handle_analyst_selection(message)

        initialize_components()

        # Parse ticker(s) from message - detect multiple tickers for portfolio mode
        ticker_matches = re.findall(r'\b([A-Z]{2,5})\b', message)
        if not ticker_matches:
            return jsonify({
                'response': "I couldn't find a stock ticker. Please include it in CAPS (e.g., NVDA, AAPL)",
                'waiting_for': 'initial_setup'
            })

        # Check if multiple tickers found - enable portfolio mode
        global portfolio_mode, portfolio_tickers, current_portfolio_ticker_index, portfolio_trade_date

        if len(ticker_matches) > 1:
            # PORTFOLIO MODE: Multiple stocks detected
            portfolio_mode = True
            portfolio_tickers = ticker_matches
            current_portfolio_ticker_index = 0
            portfolio_trade_date = datetime.now().strftime("%Y-%m-%d")
            ticker = portfolio_tickers[0]  # Start with first ticker

            print(f"[PORTFOLIO] Portfolio mode activated: {len(portfolio_tickers)} stocks: {', '.join(portfolio_tickers)}", flush=True)
        else:
            # Single stock mode
            ticker = ticker_matches[0]
            portfolio_mode = False

        trade_date = portfolio_trade_date if portfolio_mode else datetime.now().strftime("%Y-%m-%d")

        # Use selected analysts or default to market only
        selected_analysts = selected_analysts_choice if selected_analysts_choice else ["market", "fundamentals", "news"]

        print(f"[SETUP] Initializing for {ticker} with analysts: {selected_analysts}...", flush=True)

        # Check if comprehensive_quantitative is selected - if yes, ask for optimization preferences
        if 'comprehensive_quantitative' in selected_analysts:
            # Store pending data
            pending_ticker = ticker
            pending_analysts = selected_analysts
            pending_user_message = message
            waiting_for = 'optimization_preference'

            print(f"[SETUP] Comprehensive Quantitative analyst selected, asking for optimization preferences...", flush=True)

            return jsonify({
                'response': f"""**Stock: {ticker}**

Before running the Comprehensive Quantitative Analysis, please tell me your investment preferences:

**Risk Tolerance**: Conservative / Balanced / Aggressive?
**Investment Goal**: Capital preservation / Steady growth / Maximum returns?
**Time Horizon**: Short-term (< 1 year) / Medium-term (1-3 years) / Long-term (> 3 years)?
**Special Constraints**: Any specific requirements (liquidity, sector limits, etc.)?

**Example**: "I prefer balanced risk with steady growth over 2-3 years, no specific constraints"
""",
                'waiting_for': 'optimization_preference'
            })

        # Otherwise continue normally...

        # Initialize workflow
        controller.initialize(
            company_of_interest=ticker,
            trade_date=trade_date,
            selected_analysts=selected_analysts,
            user_preference_text=message
        )

        # Get preferences summary
        prefs = controller.workflow_state.user_preferences
        prefs_text = ""
        if prefs and (prefs.focus_areas or prefs.principles):
            prefs_text = "\n\nYour preferences:\n"
            if prefs.focus_areas:
                prefs_text += f"- Focus: {', '.join(prefs.focus_areas)}\n"
            if prefs.risk_tolerance:
                prefs_text += f"- Risk tolerance: {prefs.risk_tolerance}\n"

        # Get analyst name for display
        first_analyst = selected_analysts[0]
        analyst_display_names = {
            "market": "Market/Technical",
            "fundamentals": "Fundamentals",
            "news": "News",
            "social": "Social Media",
            "quantitative": "Quantitative (ML/GARCH)",
            "comprehensive_quantitative": "Multi-Scenario Optimizer",
            "visualizer": "Visualizer"
        }
        first_analyst_name = analyst_display_names.get(first_analyst, first_analyst.title())

        # Build response - add portfolio mode message if applicable
        if portfolio_mode:
            response = f"""**📊 PORTFOLIO MODE ACTIVATED**

Analyzing {len(portfolio_tickers)} stocks: **{', '.join(portfolio_tickers)}**

Starting with stock **{current_portfolio_ticker_index + 1} of {len(portfolio_tickers)}: {ticker}**

{prefs_text}

Running {first_analyst_name} Analyst...

"""
        else:
            response = f"Analysis started for **{ticker}**{prefs_text}\n\nRunning {first_analyst_name} Analyst...\n\n"

        print(f"[ANALYST] Running {first_analyst} analyst...", flush=True)

        # Run first analyst
        result = controller.run_current_analyst()

        if "error" in result:
            return jsonify({
                'response': f"Error: {result['error']}",
                'waiting_for': None
            })

        current_analyst = result['analyst']
        current_analyst_display = analyst_display_names.get(current_analyst, current_analyst.title())

        print(f"[ANALYST] {current_analyst} completed in {result.get('duration', 0):.1f}s", flush=True)
        print(f"[REPORT] Length: {len(result['report'])} chars", flush=True)

        analyst_response = f"""---

## {current_analyst_display} Analyst Report

{result['report']}

---

**What would you like to do?**

Type:
- **"approved"** or **"ok"** to continue to next analyst
- **Specific feedback** to request revision (e.g., "Focus more on RSI indicators")
"""

        waiting_for = 'feedback'

        return jsonify({
            'response': response + analyst_response,
            'waiting_for': 'feedback'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def handle_feedback(message):
    """Handle user feedback"""
    global waiting_for, current_analyst

    try:
        print(f"[FEEDBACK] Processing feedback: {message[:50]}...", flush=True)
        print(f"[FEEDBACK] Current analyst index BEFORE: {controller.workflow_state.current_analyst_index}", flush=True)
        print(f"[FEEDBACK] Total analysts: {len(controller.workflow_state.selected_analysts)}", flush=True)
        print(f"[FEEDBACK] Selected analysts: {controller.workflow_state.selected_analysts}", flush=True)

        # Process feedback
        analysis = controller.process_feedback(message)

        print(f"[FEEDBACK] Action: {analysis.action.value}", flush=True)
        print(f"[FEEDBACK] Current analyst index AFTER process_feedback: {controller.workflow_state.current_analyst_index}", flush=True)

        if analysis.action == FeedbackAction.APPROVE:
            is_complete = controller.workflow_state.is_complete()
            print(f"[FEEDBACK] is_complete() returned: {is_complete}", flush=True)

            # Check if complete
            if is_complete:
                print("[COMPLETE] All analysts done, asking user if they want final decision...", flush=True)
                waiting_for = "final_decision"

                # List completed analysts
                completed_list = "\n".join([f"✅ {analyst}" for analyst in controller.workflow_state.selected_analysts])

                return jsonify({
                    'response': f"**All Analysts Completed!**\n\n{completed_list}\n\n---\n\n**Would you like to generate the final investment decision and comprehensive report?**\n\nType **'yes'** to generate the final decision, or **'no'** to review individual analyst reports.",
                    'waiting_for': waiting_for
                })

            # Run next analyst
            next_analyst = controller.workflow_state.get_current_analyst()
            analyst_names = {
                "market": "Market/Technical",
                "fundamentals": "Fundamentals",
                "news": "News",
                "social": "Social Media",
                "quantitative": "Quantitative (ML/GARCH)",
                "comprehensive_quantitative": "Multi-Scenario Optimizer",
                "visualizer": "Visualizer"
            }

            print(f"[ANALYST] Running {next_analyst} analyst...", flush=True)

            response = f"Approved! Moving to next analyst...\n\n{analyst_names.get(next_analyst, next_analyst)} Analyst running...\n\n"

            result = controller.run_current_analyst()

            if "error" in result:
                return jsonify({'error': result['error']}), 500

            current_analyst = result['analyst']

            print(f"[ANALYST] {current_analyst} completed in {result.get('duration', 0):.1f}s", flush=True)

            analyst_response = f"""---

## {analyst_names.get(current_analyst, current_analyst)} Analyst Report

{result['report']}

---

**What would you like to do?**

Type:
- **"approved"** or **"ok"** to continue
- **Specific feedback** to request revision
"""

            return jsonify({
                'response': response + analyst_response,
                'waiting_for': 'feedback'
            })

        elif analysis.action == FeedbackAction.REVISE:
            # REVISE: User wants significant changes - rerun the analyst
            print(f"[REVISION] Rerunning {current_analyst} with feedback...", flush=True)

            # Check if user wants to change optimization method (for comprehensive_quantitative)
            if current_analyst == 'comprehensive_quantitative':
                message_lower = message.lower()

                # Detect direct method specification
                method_keywords = {
                    'mean_variance': ['mean_variance', 'mean-variance', 'mean variance', 'markowitz'],
                    'risk_parity': ['risk_parity', 'risk-parity', 'risk parity', 'parity'],
                    'min_variance': ['min_variance', 'min-variance', 'min variance', 'minimum variance', 'minimum-variance'],
                    'max_sharpe': ['max_sharpe', 'max-sharpe', 'max sharpe', 'maximum sharpe', 'maximum-sharpe', 'sharpe ratio', 'sharpe-ratio', 'use sharpe'],
                    'equal_weight': ['equal_weight', 'equal-weight', 'equal weight']
                }

                detected_method = None
                for method, keywords in method_keywords.items():
                    if any(keyword in message_lower for keyword in keywords):
                        detected_method = method
                        break

                # Update optimization_method_choice if new method detected
                if detected_method:
                    print(f"[REVISION] Detected method change request: {detected_method}", flush=True)

                    scenario_map = {
                        'mean_variance': ['conservative', 'moderate', 'aggressive', 'sharpe_optimized'],
                        'risk_parity': ['equal_risk', 'vol_weighted', 'sharpe_weighted', 'cvar_weighted'],
                        'min_variance': ['pure_min_var', 'cvar_constraint', 'turnover_constraint', 'sector_constraint'],
                        'max_sharpe': ['unconstrained', 'long_only', 'box_constraints', 'tracking_error'],
                        'equal_weight': ['pure_equal', 'vol_adjusted', 'risk_budget']
                    }

                    # Update the stored optimization choice
                    controller.workflow_state.agent_state['optimization_method_choice'] = {
                        'selected_method': detected_method,
                        'rationale': f'User requested {detected_method} optimization method via feedback',
                        'risk_tolerance': 'moderate',
                        'scenarios': scenario_map[detected_method],
                        'user_preference_text': message
                    }

                    print(f"[REVISION] Updated optimization_method_choice to: {detected_method}", flush=True)

            response = f"Revision requested\n\nRevision instructions: {analysis.revision_instructions}\n\nRe-running {current_analyst} analyst...\n\n"

            result = controller.run_current_analyst()

            if "error" in result:
                return jsonify({'error': result['error']}), 500

            analyst_response = f"""---

## {current_analyst.title()} Analyst Report (Revised)

{result['report']}

---

**What would you like to do?**

Type:
- **"approved"** or **"ok"** to continue
- **More feedback** for another revision
"""

            return jsonify({
                'response': response + analyst_response,
                'waiting_for': 'feedback'
            })

        elif analysis.action == FeedbackAction.CLARIFY or analysis.action == FeedbackAction.EXPAND:
            # User is asking a question about the report - answer it conversationally
            print(f"[CLARIFY] Answering user question: {message[:50]}...", flush=True)

            # Get current report
            analyst_status = controller.workflow_state.analyst_statuses[current_analyst]
            current_report = analyst_status.report

            # Collect all completed analyst reports for cross-analyst questions
            all_reports_text = ""
            analyst_name_map = {
                "market": "Market/Technical Analysis",
                "fundamentals": "Fundamental Analysis",
                "news": "News Sentiment Analysis",
                "social": "Social Media Sentiment Analysis",
                "quantitative": "Quantitative Analysis (ML/GARCH)",
                "comprehensive_quantitative": "Multi-Scenario Optimization",
                "visualizer": "Visualization Analysis"
            }

            for analyst_type in controller.workflow_state.selected_analysts:
                status = controller.workflow_state.analyst_statuses[analyst_type]
                # Include ANY analyst that has a report, regardless of status (completed, review, etc.)
                if status.report and status.report.strip():
                    analyst_name = analyst_name_map.get(analyst_type, analyst_type.title())
                    all_reports_text += f"\n\n## {analyst_name} Report:\n\n{status.report}\n"
                    all_reports_text += "\n" + "="*80 + "\n"

            # Use LLM to answer the question based on ALL reports
            try:
                llm = controller.graph.quick_thinking_llm

                answer_prompt = f"""You are a financial analyst assistant. A user is asking a question about the analysis reports.

You have access to ALL completed analyst reports below. The user may be asking about data from ANY of these reports, so review all of them carefully.

**ALL COMPLETED ANALYST REPORTS:**
{all_reports_text}

**Current Analyst Being Reviewed:** {current_analyst}

**User's Question:**
{message}

**Instructions:**
- Answer the user's question directly based on ANY of the available reports above
- If the question involves data from multiple analysts (e.g., comparing technical and fundamental metrics), synthesize information from ALL relevant reports
- Be concise but thorough
- Use specific numbers and details from the reports
- Cite which analyst report the information comes from (e.g., "According to the Market/Technical Analysis, ATR is...")
- If the information isn't in any of the reports, say so clearly

**Answer:**"""

                answer = llm.invoke(answer_prompt)
                answer_text = answer.content if hasattr(answer, 'content') else str(answer)

                response = f"""{answer_text}

---

**What would you like to do?**

Type:
- **Ask more questions** about this report
- **"approved"** or **"ok"** to continue to next analyst
- **Specific feedback** to request revision
"""

                return jsonify({
                    'response': response,
                    'waiting_for': 'feedback'
                })

            except Exception as e:
                print(f"[ERROR] Failed to answer question: {str(e)}", flush=True)
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'Failed to answer question: {str(e)}'}), 500

        else:
            # Unknown action
            return jsonify({
                'response': f"I didn't understand that feedback. Please type 'approved' to continue, or provide specific feedback for revision.",
                'waiting_for': 'feedback'
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def handle_optimization_preference(message):
    """Handle user's optimization preference and use LLM to select method"""
    global waiting_for, current_analyst, pending_ticker, pending_analysts, pending_user_message, portfolio_mode, portfolio_optimization_preference

    try:
        print(f"[OPTIMIZATION] Analyzing preferences: {message[:50]}...", flush=True)

        # Check if user directly specified a method
        message_lower = message.lower()
        direct_method = None
        if 'mean_variance' in message_lower or 'mean variance' in message_lower:
            direct_method = 'mean_variance'
        elif 'risk_parity' in message_lower or 'risk parity' in message_lower:
            direct_method = 'risk_parity'
        elif 'min_variance' in message_lower or 'minimum variance' in message_lower or 'min variance' in message_lower:
            direct_method = 'min_variance'
        elif 'max_sharpe' in message_lower or 'maximum sharpe' in message_lower or 'max sharpe' in message_lower:
            direct_method = 'max_sharpe'
        elif 'equal_weight' in message_lower or 'equal weight' in message_lower:
            direct_method = 'equal_weight'

        if direct_method:
            print(f"[OPTIMIZATION] User directly specified method: {direct_method}", flush=True)
            # Use predefined scenarios for the specified method
            scenario_map = {
                'mean_variance': ['conservative', 'moderate', 'aggressive', 'sharpe_optimized'],
                'risk_parity': ['equal_risk', 'vol_weighted', 'sharpe_weighted', 'cvar_weighted'],
                'min_variance': ['pure_min_var', 'cvar_constraint', 'turnover_constraint', 'sector_constraint'],
                'max_sharpe': ['unconstrained', 'long_only', 'box_constraints', 'tracking_error'],
                'equal_weight': ['pure_equal', 'vol_adjusted', 'risk_budget']
            }
            choice_data = {
                'selected_method': direct_method,
                'rationale': f'User directly requested {direct_method} optimization method',
                'risk_tolerance': 'moderate',
                'scenarios': scenario_map[direct_method],
                'user_preference_text': message
            }
            print(f"[OPTIMIZATION] Skipping LLM, using direct method selection", flush=True)
        else:
            # Get the LLM for analysis
            llm = controller.graph.quick_thinking_llm
            print("[OPTIMIZATION] Calling LLM to analyze preferences...", flush=True)

            # Create prompt for LLM to analyze preferences and select method
            analysis_prompt = f"""Analyze the following investment preferences and select the most suitable portfolio optimization method.

User Preferences: {message}

Available Methods:
1. **mean_variance**: Markowitz Mean-Variance Optimization - Balances expected return vs risk (variance). Best for investors who want to optimize return for a given risk level or minimize risk for a target return.

2. **risk_parity**: Risk Parity - Equalizes risk contribution across assets. Best for investors who want balanced risk distribution regardless of asset allocation percentages.

3. **min_variance**: Minimum Variance - Minimizes portfolio volatility. Best for conservative investors focused on capital preservation and minimizing drawdowns.

4. **max_sharpe**: Maximum Sharpe Ratio - Optimizes risk-adjusted returns (return per unit of risk). Best for investors seeking the best risk-reward tradeoff.

5. **equal_weight**: Equal Weight - Simple equal allocation across all positions. Best as a benchmark or for investors who prefer simplicity and don't want to make active allocation decisions.

Based on the user's stated preferences, select the MOST APPROPRIATE method and provide:
- The method name (exactly one of: mean_variance, risk_parity, min_variance, max_sharpe, equal_weight)
- A brief rationale (1-2 sentences) explaining why this method fits their preferences
- The user's risk tolerance level (conservative, moderate, or aggressive)
- 4 scenario names to run for this method (these will be used as parameter variations)

Respond ONLY with valid JSON in this exact format:
{{
    "selected_method": "method_name",
    "rationale": "explanation here",
    "risk_tolerance": "conservative/moderate/aggressive",
    "scenarios": ["scenario1", "scenario2", "scenario3", "scenario4"]
}}

For scenarios, use method-appropriate names:
- For mean_variance: ["conservative", "moderate", "aggressive", "sharpe_optimized"]
- For risk_parity: ["equal_risk", "vol_weighted", "sharpe_weighted", "cvar_weighted"]
- For min_variance: ["pure_min_var", "cvar_constraint", "turnover_constraint", "sector_constraint"]
- For max_sharpe: ["unconstrained", "long_only", "box_constraints", "tracking_error"]
- For equal_weight: ["pure_equal", "vol_adjusted", "risk_budget"]

IMPORTANT: Return ONLY the JSON object, no other text."""

            # Get LLM response
            response = llm.invoke(analysis_prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)

            print(f"[OPTIMIZATION] LLM response: {response_text[:200]}...", flush=True)

            # Parse JSON response
            import json
            import re

            # Try to extract JSON from response
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if not json_match:
                # Fallback: use mean_variance as default
                choice_data = {
                    'selected_method': 'mean_variance',
                    'rationale': 'Default method selected due to parsing error',
                    'risk_tolerance': 'moderate',
                    'scenarios': ['conservative', 'moderate', 'aggressive', 'sharpe_optimized']
                }
                print("[OPTIMIZATION] Failed to parse LLM response, using default mean_variance", flush=True)
            else:
                try:
                    choice_data = json.loads(json_match.group(0))
                    print(f"[OPTIMIZATION] Selected method: {choice_data.get('selected_method')}", flush=True)
                except json.JSONDecodeError:
                    # Fallback
                    choice_data = {
                        'selected_method': 'mean_variance',
                        'rationale': 'Default method selected due to JSON parsing error',
                        'risk_tolerance': 'moderate',
                        'scenarios': ['conservative', 'moderate', 'aggressive', 'sharpe_optimized']
                    }
                    print("[OPTIMIZATION] JSON decode failed, using default mean_variance", flush=True)

            # Add user's original preference text
            choice_data['user_preference_text'] = message

        # Now initialize the controller with pending data
        trade_date = datetime.now().strftime("%Y-%m-%d")

        print(f"[OPTIMIZATION] Initializing controller for {pending_ticker}...", flush=True)
        controller.initialize(
            company_of_interest=pending_ticker,
            trade_date=trade_date,
            selected_analysts=pending_analysts,
            user_preference_text=pending_user_message
        )

        # Store optimization choice in workflow state
        controller.workflow_state.agent_state['optimization_method_choice'] = choice_data
        print(f"[OPTIMIZATION] Stored optimization choice: {choice_data}", flush=True)

        # PORTFOLIO MODE: Save optimization preference globally for reuse on subsequent stocks
        global portfolio_optimization_preference
        if portfolio_mode:
            portfolio_optimization_preference = choice_data.copy()
            print(f"[PORTFOLIO] Saved optimization preference for portfolio stocks", flush=True)

        # Get analyst display names
        analyst_display_names = {
            "market": "Market/Technical",
            "fundamentals": "Fundamentals",
            "news": "News",
            "social": "Social Media",
            "quantitative": "Quantitative (ML/GARCH)",
            "comprehensive_quantitative": "Multi-Scenario Optimizer",
            "visualizer": "Visualizer"
        }

        # Get first analyst
        first_analyst = pending_analysts[0]
        first_analyst_name = analyst_display_names.get(first_analyst, first_analyst.title())

        # Build response
        method_name_display = {
            'mean_variance': 'Mean-Variance Optimization',
            'risk_parity': 'Risk Parity',
            'min_variance': 'Minimum Variance',
            'max_sharpe': 'Maximum Sharpe Ratio',
            'equal_weight': 'Equal Weight'
        }

        response_text = f"""**Optimization Method Selected**: {method_name_display.get(choice_data['selected_method'], choice_data['selected_method'])}

**Rationale**: {choice_data['rationale']}

**Risk Profile**: {choice_data['risk_tolerance'].title()}

**Scenarios to Analyze**: {', '.join(choice_data['scenarios'])}

---

Analysis started for **{pending_ticker}**

Running {first_analyst_name} Analyst...

"""

        print(f"[ANALYST] Running {first_analyst} analyst...", flush=True)

        # Run first analyst
        result = controller.run_current_analyst()

        if "error" in result:
            return jsonify({
                'response': f"Error: {result['error']}",
                'waiting_for': None
            })

        current_analyst = result['analyst']
        current_analyst_display = analyst_display_names.get(current_analyst, current_analyst.title())

        print(f"[ANALYST] {current_analyst} completed in {result.get('duration', 0):.1f}s", flush=True)
        print(f"[REPORT] Length: {len(result['report'])} chars", flush=True)

        analyst_response = f"""---

## {current_analyst_display} Analyst Report

{result['report']}

---

**What would you like to do?**

Type:
- **"approved"** or **"ok"** to continue to next analyst
- **Specific feedback** to request revision (e.g., "Focus more on RSI indicators")
"""

        waiting_for = 'feedback'

        # Clear pending variables
        pending_ticker = None
        pending_analysts = None
        pending_user_message = None

        # Check if visualizer analyst returned a chart
        chart_url = None
        if current_analyst == 'visualizer' and 'chart_data' in result:
            chart_path = result.get('chart_data', {}).get('chart_path', '')
            if chart_path:
                # Convert Windows path to URL format
                chart_path = chart_path.replace('\\', '/')
                # Remove 'results/' prefix if present
                if chart_path.startswith('results/'):
                    chart_path = chart_path[8:]  # Remove 'results/'
                chart_url = f"/api/charts/{chart_path}"
                print(f"[CHART] Generated URL: {chart_url}", flush=True)

        response_data = {
            'response': response_text + analyst_response,
            'waiting_for': 'feedback'
        }

        # Add chart URL if available
        if chart_url:
            response_data['chart_url'] = chart_url

        return jsonify(response_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def generate_reports(controller):
    """Generate comprehensive Word and Markdown reports after analysis completion"""
    try:
        state = controller.workflow_state.agent_state
        ticker = state.get('company_of_interest', 'UNKNOWN')
        current_date = state.get('trade_date', datetime.now().strftime('%Y-%m-%d'))

        # Collect all analyst reports
        market_report = state.get('market_report', '')
        news_report = state.get('news_report', '')
        sentiment_report = state.get('sentiment_report', '')
        fundamentals_report = state.get('fundamentals_report', '')
        quantitative_report = state.get('quantitative_report', '') or state.get('comprehensive_quantitative_report', '')
        final_decision = state.get('trader_investment_plan', '')

        # Find chart path if visualizer was used
        chart_paths = None
        results_dir = Path(project_root) / 'results' / ticker / current_date
        potential_chart = results_dir / f"{ticker}_comprehensive_analysis_{current_date}.png"
        if potential_chart.exists():
            chart_paths = [str(potential_chart)]

        print(f"[REPORT_GEN] Generating reports for {ticker} on {current_date}", flush=True)

        # Generate Word document
        word_doc_path = generate_comprehensive_word_report(
            ticker=ticker,
            current_date=current_date,
            market_report=market_report,
            news_report=news_report,
            sentiment_report=sentiment_report,
            fundamentals_report=fundamentals_report,
            quantitative_report=quantitative_report,
            final_decision=final_decision,
            chart_paths=chart_paths
        )

        print(f"[REPORT_GEN] Word document created: {word_doc_path}", flush=True)

        # Generate Markdown version
        markdown_path = generate_markdown_report(
            ticker=ticker,
            current_date=current_date,
            market_report=market_report,
            news_report=news_report,
            sentiment_report=sentiment_report,
            fundamentals_report=fundamentals_report,
            quantitative_report=quantitative_report,
            final_decision=final_decision
        )

        print(f"[REPORT_GEN] Markdown document created: {markdown_path}", flush=True)

        return {
            'word': str(word_doc_path),
            'markdown': str(markdown_path)
        }

    except Exception as e:
        print(f"[ERROR] Report generation failed: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return {}


def generate_markdown_report(ticker, current_date, market_report, news_report,
                             sentiment_report, fundamentals_report,
                             quantitative_report, final_decision):
    """Generate a markdown version of the comprehensive report"""

    # Build markdown content with enhanced formatting
    markdown_content = f"""<div align="center">

# 📊 {ticker} Comprehensive Trading Analysis Report

**Analysis Date:** {current_date}
**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

</div>

## 📑 Table of Contents

1. [Executive Summary & Trading Decision](#executive-summary--trading-decision)
2. [📈 Technical Analysis](#-technical-analysis)
3. [📰 News Analysis](#-news-analysis)
4. [💭 Sentiment Analysis](#-sentiment-analysis)
5. [📊 Fundamental Analysis](#-fundamental-analysis)
6. [🔢 Quantitative Analysis](#-quantitative-analysis)
7. [Final Recommendations](#final-recommendations)

---

## 🎯 Executive Summary & Trading Decision

<div style="background-color: #f0f8ff; padding: 20px; border-left: 4px solid #00d9ff; margin: 10px 0;">

{final_decision if final_decision else '**No final decision available**'}

</div>

### Quick Analysis Overview

| Analysis Type | Status | Key Finding |
|---------------|--------|-------------|
| **Technical** | ✅ Complete | See detailed technical analysis below |
| **News & Sentiment** | ✅ Complete | See news and sentiment sections |
| **Fundamentals** | ✅ Complete | See fundamental analysis tables |
| **Quantitative** | ✅ Complete | See statistical modeling results |

---

## 📈 Technical Analysis

<div style="border: 2px solid #00d9ff; padding: 15px; border-radius: 8px; margin: 10px 0;">

{market_report if market_report else '**No market analysis available**'}

</div>

**[⬆️ Back to Top](#-table-of-contents)**

---

## 📰 News Analysis

<div style="border: 2px solid #4CAF50; padding: 15px; border-radius: 8px; margin: 10px 0;">

{news_report if news_report else '**No news analysis available**'}

</div>

**[⬆️ Back to Top](#-table-of-contents)**

---

## 💭 Sentiment Analysis

<div style="border: 2px solid #FF9800; padding: 15px; border-radius: 8px; margin: 10px 0;">

{sentiment_report if sentiment_report else '**No sentiment analysis available**'}

</div>

**[⬆️ Back to Top](#-table-of-contents)**

---

## 📊 Fundamental Analysis

<div style="border: 2px solid #9C27B0; padding: 15px; border-radius: 8px; margin: 10px 0;">

{fundamentals_report if fundamentals_report else '**No fundamental analysis available**'}

</div>

**[⬆️ Back to Top](#-table-of-contents)**

---

## 🔢 Quantitative Analysis

<div style="border: 2px solid #F44336; padding: 15px; border-radius: 8px; margin: 10px 0;">

{quantitative_report if quantitative_report else '**No quantitative analysis available**'}

</div>

**[⬆️ Back to Top](#-table-of-contents)**

---

## 🎁 Final Recommendations

### Investment Checklist

- [ ] Review the Executive Summary trading decision
- [ ] Verify technical indicators support the decision
- [ ] Check news and sentiment alignment
- [ ] Confirm fundamental health metrics
- [ ] Validate quantitative models
- [ ] Set appropriate entry/exit points
- [ ] Establish stop-loss levels
- [ ] Monitor ongoing developments

### Risk Management Reminders

⚠️ **Important Notes:**
- This report is for informational purposes only
- Always conduct your own due diligence
- Past performance does not guarantee future results
- Consider your risk tolerance and investment goals
- Consult with a financial advisor if needed

---

<div align="center">

**📄 Report End**

*Generated by AI Trading Analysis System*
*Powered by WatsonX AI & Multi-Agent Analysis Framework*

**[⬆️ Back to Top](#-table-of-contents)**

</div>
"""

    # Save markdown file
    results_dir = Path(project_root) / 'results' / ticker / current_date
    results_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = results_dir / f"{ticker}_comprehensive_report_{current_date}.md"

    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    return markdown_path


def handle_final_decision_request(message):
    """Handle user's response to final decision generation prompt"""
    global waiting_for, portfolio_mode, portfolio_results, current_portfolio_ticker_index, portfolio_tickers

    message_lower = message.lower().strip()

    # Check if user wants final decision
    if message_lower in ['yes', 'y', 'generate', 'ok', '是', '好', 'approved']:
        print("[FINAL_DECISION] User approved, generating final decision...", flush=True)

        try:
            # Get final decision
            final = controller.get_final_decision()

            # Generate comprehensive reports
            print("[REPORT_GEN] Generating comprehensive reports...", flush=True)
            report_files = generate_reports(controller)

            # CHECK IF PORTFOLIO MODE
            if portfolio_mode:
                # Save current stock's results
                current_ticker = portfolio_tickers[current_portfolio_ticker_index]
                portfolio_results[current_ticker] = {
                    'state': controller.workflow_state.agent_state.copy(),
                    'report': final,
                    'decision': controller.workflow_state.agent_state.get('trader_investment_plan', ''),
                    'report_files': report_files
                }
                print(f"[PORTFOLIO] Saved results for {current_ticker}", flush=True)

                # CRITICAL FIX: Export CSV data for portfolio optimization
                try:
                    from tradingagents.portfolio.csv_data_exporter import CSVDataExporter
                    csv_exporter = CSVDataExporter(current_ticker, portfolio_trade_date)
                    exported_files = csv_exporter.export_all_data(controller.workflow_state.agent_state)
                    print(f"[PORTFOLIO] Exported {len(exported_files)} CSV files for {current_ticker}", flush=True)
                except Exception as e:
                    print(f"[PORTFOLIO] Warning: Failed to export CSV for {current_ticker}: {str(e)}", flush=True)

                # Check if more stocks to analyze
                if current_portfolio_ticker_index + 1 < len(portfolio_tickers):
                    # More stocks remain - ask user if they want to continue
                    next_ticker = portfolio_tickers[current_portfolio_ticker_index + 1]
                    waiting_for = 'next_stock_prompt'

                    response_text = f"""✅ **{current_ticker} Analysis Complete!**

---

## 📊 Final Analysis Report

{final}

---

**📊 Portfolio Progress: {current_portfolio_ticker_index + 1} of {len(portfolio_tickers)} stocks completed**

✅ Completed: {', '.join(portfolio_tickers[:current_portfolio_ticker_index + 1])}
⏳ Remaining: {', '.join(portfolio_tickers[current_portfolio_ticker_index + 1:])}

---

**Would you like to analyze the next stock ({next_ticker})?**

Type **'yes'** to continue, or **'no'** to stop and generate portfolio with current results.
"""

                    return jsonify({
                        'response': response_text,
                        'waiting_for': 'next_stock_prompt'
                    })
                else:
                    # All stocks complete - show final stock report FIRST, then trigger portfolio
                    print(f"[PORTFOLIO] All {len(portfolio_tickers)} stocks complete!", flush=True)

                    response_text = f"""✅ **{current_ticker} Analysis Complete!**

---

## 📊 Final Analysis Report

{final}

---

**📊 All {len(portfolio_tickers)} stocks analyzed!**

✅ Completed: {', '.join(portfolio_tickers)}

"""
                    # Add report files info if available
                    if report_files:
                        response_text += "## 📄 Generated Reports for " + current_ticker + "\n\n"
                        if 'word' in report_files:
                            word_filename = Path(report_files['word']).name
                            response_text += f"- **Word Document**: `{word_filename}`\n"
                        if 'markdown' in report_files:
                            markdown_filename = Path(report_files['markdown']).name
                            response_text += f"- **Markdown Report**: `{markdown_filename}`\n"
                        response_text += f"\n*Reports saved to: `{Path(report_files.get('word', '')).parent}`*\n\n"

                    response_text += """---

**Ready to generate portfolio optimization report!**

Generating comprehensive multi-stock portfolio analysis...
"""

                    # Now trigger portfolio optimization
                    print(f"[PORTFOLIO] Generating portfolio report...", flush=True)
                    portfolio_response = handle_portfolio_optimization()

                    # Append portfolio report to the response
                    if isinstance(portfolio_response, tuple):
                        portfolio_data = portfolio_response[0].get_json()
                    else:
                        portfolio_data = portfolio_response.get_json()

                    response_text += "\n\n" + portfolio_data.get('response', '')

                    return jsonify({
                        'response': response_text,
                        'waiting_for': None
                    })
            else:
                # SINGLE STOCK MODE - normal flow
                waiting_for = None

                # Build response with report download links
                response_text = f"{final}\n\n---\n\n**Analysis complete!**\n\n"

                if report_files:
                    response_text += "## 📄 Generated Reports\n\n"
                    if 'word' in report_files:
                        word_filename = Path(report_files['word']).name
                        response_text += f"- **Word Document**: `{word_filename}`\n"
                    if 'markdown' in report_files:
                        markdown_filename = Path(report_files['markdown']).name
                        response_text += f"- **Markdown Report**: `{markdown_filename}`\n"
                    response_text += f"\n*Reports saved to: `{Path(report_files.get('word', '')).parent}`*\n"

                return jsonify({
                    'response': response_text,
                    'waiting_for': None,
                    'report_files': report_files
                })
        except Exception as e:
            print(f"[ERROR] Failed to generate final decision: {str(e)}", flush=True)
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Failed to generate final decision: {str(e)}'}), 500
    else:
        print("[FINAL_DECISION] User declined final decision generation", flush=True)
        waiting_for = None

        # List available reports
        analyst_names_map = {
            'comprehensive_quantitative': 'Comprehensive Quantitative Analysis',
            'market': 'Market/Technical Analysis',
            'fundamentals': 'Fundamental Analysis',
            'news': 'News Analysis',
            'social': 'Social Media Analysis',
            'quantitative': 'Quantitative Analysis (ML/GARCH)',
            'visualizer': 'Visualizer'
        }

        completed_analysts = controller.workflow_state.selected_analysts
        completed_reports = "\n".join([
            f"- {analyst_names_map.get(a, a.title())}"
            for a in completed_analysts
        ])

        return jsonify({
            'response': f"**Understood!** You can review the individual analyst reports:\n\n{completed_reports}\n\n---\n\nTo start a new analysis, type **'start over'** or refresh the page.",
            'waiting_for': None
        })


def handle_next_stock_prompt(message):
    """Handle user's response to continuing with next stock in portfolio"""
    global waiting_for, current_portfolio_ticker_index, portfolio_tickers, selected_analysts_choice, portfolio_trade_date, portfolio_optimization_preference

    message_lower = message.lower().strip()

    if message_lower in ['yes', 'y', 'continue', 'ok', '是', '好']:
        # User wants to analyze next stock
        current_portfolio_ticker_index += 1
        next_ticker = portfolio_tickers[current_portfolio_ticker_index]

        print(f"[PORTFOLIO] Starting analysis for stock {current_portfolio_ticker_index + 1}/{len(portfolio_tickers)}: {next_ticker}", flush=True)

        # Initialize controller for next stock
        controller.initialize(
            company_of_interest=next_ticker,
            trade_date=portfolio_trade_date,
            selected_analysts=selected_analysts_choice,
            user_preference_text=f"Portfolio analysis for {next_ticker}"
        )

        # CRITICAL: Reset analyst index to 0 for new stock (initialize() doesn't reset this)
        controller.workflow_state.current_analyst_index = 0
        print(f"[PORTFOLIO] Reset analyst index to 0 for {next_ticker}", flush=True)

        # PORTFOLIO MODE: Inject saved optimization preference to avoid re-asking
        if portfolio_optimization_preference:
            controller.workflow_state.agent_state['optimization_method_choice'] = portfolio_optimization_preference.copy()
            print(f"[PORTFOLIO] Reusing optimization preference from first stock: {portfolio_optimization_preference.get('selected_method', 'unknown')}", flush=True)

        # Get analyst display names
        analyst_display_names = {
            "market": "Market/Technical",
            "fundamentals": "Fundamentals",
            "news": "News",
            "social": "Social Media",
            "quantitative": "Quantitative (ML/GARCH)",
            "comprehensive_quantitative": "Multi-Scenario Optimizer",
            "visualizer": "Visualizer"
        }

        first_analyst = selected_analysts_choice[0]
        first_analyst_name = analyst_display_names.get(first_analyst, first_analyst.title())

        response_text = f"""**📊 Continuing Portfolio Analysis**

Stock **{current_portfolio_ticker_index + 1} of {len(portfolio_tickers)}: {next_ticker}**

Running {first_analyst_name} Analyst...

"""

        print(f"[ANALYST] Running {first_analyst} analyst for {next_ticker}...", flush=True)

        # Run first analyst with retry logic for short/invalid reports
        max_retries = 2
        result = None
        for attempt in range(max_retries):
            result = controller.run_current_analyst()

            if "error" in result:
                return jsonify({
                    'response': f"Error: {result['error']}",
                    'waiting_for': None
                })

            # Validate report length (detect mathematical notation like $\boxed{BUY}$)
            report_length = len(result.get('report', ''))
            if report_length < 500:
                print(f"[PORTFOLIO] WARNING: {result['analyst']} report too short ({report_length} chars), likely invalid output", flush=True)
                if attempt < max_retries - 1:
                    print(f"[PORTFOLIO] Retrying {result['analyst']} (attempt {attempt + 2}/{max_retries})...", flush=True)
                    # Reset analyst to retry
                    controller.workflow_state.current_analyst_index -= 1
                    continue
                else:
                    print(f"[PORTFOLIO] Max retries reached, using short report", flush=True)
            break

        current_analyst = result['analyst']
        current_analyst_display = analyst_display_names.get(current_analyst, current_analyst.title())

        print(f"[ANALYST] {current_analyst} completed in {result.get('duration', 0):.1f}s", flush=True)

        analyst_response = f"""---

## {current_analyst_display} Analyst Report

{result['report']}

---

**What would you like to do?**

Type:
- **"approved"** or **"ok"** to continue to next analyst
- **Specific feedback** to request revision
"""

        waiting_for = 'feedback'

        return jsonify({
            'response': response_text + analyst_response,
            'waiting_for': 'feedback'
        })
    else:
        # User declined - generate portfolio with current stocks
        print(f"[PORTFOLIO] User stopped. Generating portfolio with {current_portfolio_ticker_index + 1} stocks...", flush=True)
        return handle_portfolio_optimization()


def handle_portfolio_llm_fallback(tickers):
    """Use LLM to generate portfolio analysis when optimization algorithm can't run due to partial data"""
    global portfolio_mode, portfolio_trade_date, waiting_for, selected_analysts_choice

    print(f"[PORTFOLIO_LLM] Generating LLM-based portfolio analysis with partial data...", flush=True)
    print(f"[PORTFOLIO_LLM] Available analysts: {selected_analysts_choice}", flush=True)

    try:
        # Load available CSV data for each ticker
        stocks_data = {}
        for ticker in tickers:
            csv_dir = Path(f"results/{ticker}/{portfolio_trade_date}/csv_data")
            if not csv_dir.exists():
                print(f"[PORTFOLIO_LLM] No CSV data for {ticker}", flush=True)
                continue

            ticker_data = {
                'ticker': ticker,
                'fundamentals': None,
                'technical': None,
                'sentiment': None
            }

            # Load fundamentals if available
            fin_path = csv_dir / 'financial_metrics.csv'
            if fin_path.exists():
                fin_df = pd.read_csv(fin_path)
                if not fin_df.empty:
                    ticker_data['fundamentals'] = fin_df.iloc[0].to_dict()
                    print(f"[PORTFOLIO_LLM] Loaded fundamentals for {ticker}", flush=True)

            # Load technical if available
            tech_path = csv_dir / 'technical_indicators.csv'
            if tech_path.exists():
                tech_df = pd.read_csv(tech_path)
                if not tech_df.empty:
                    ticker_data['technical'] = tech_df.iloc[0].to_dict()
                    print(f"[PORTFOLIO_LLM] Loaded technical data for {ticker}", flush=True)

            # Load sentiment if available
            sent_path = csv_dir / 'sentiment_analysis.csv'
            if sent_path.exists():
                sent_df = pd.read_csv(sent_path)
                if not sent_df.empty:
                    ticker_data['sentiment'] = sent_df.iloc[0].to_dict()
                    print(f"[PORTFOLIO_LLM] Loaded sentiment data for {ticker}", flush=True)

            stocks_data[ticker] = ticker_data

        if len(stocks_data) < 2:
            waiting_for = None
            portfolio_mode = False
            return jsonify({
                'response': f"⚠️ Could not load sufficient data for portfolio analysis. Only {len(stocks_data)} stock(s) have data.",
                'waiting_for': None
            })

        # Build comparative tables
        comparative_analysis = build_comparative_tables(stocks_data, selected_analysts_choice)

        # Use LLM to analyze and recommend
        print("[PORTFOLIO_LLM] Using LLM to generate portfolio recommendation...", flush=True)
        llm_recommendation = generate_llm_portfolio_recommendation(stocks_data, comparative_analysis, portfolio_trade_date)

        # Save report
        report_dir = Path(f"portfolio_results/{portfolio_trade_date}")
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"portfolio_analysis_llm_{portfolio_trade_date}.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(llm_recommendation)

        print(f"[PORTFOLIO_LLM] Report saved to: {report_path}", flush=True)

        # Reset portfolio mode
        portfolio_mode = False
        waiting_for = None

        summary_text = f"""✅ **PORTFOLIO ANALYSIS COMPLETE (LLM-Based)**

**Analyzed Stocks**: {', '.join(tickers)} ({len(tickers)} stocks)

**Analysis Method**: LLM-based comparative analysis
**Available Data**: {', '.join([a.capitalize() for a in selected_analysts_choice or []])}

**Report Location:** `{report_path}`

---

## Complete Portfolio Report

{llm_recommendation}

---

**📄 Full portfolio report saved to:** `{report_path}`

Portfolio analysis complete! You can start a new analysis by typing 'start over' or refreshing the page.
"""

        return jsonify({
            'response': summary_text,
            'waiting_for': None
        })

    except Exception as e:
        print(f"[ERROR] Portfolio LLM fallback failed: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        waiting_for = None
        portfolio_mode = False
        return jsonify({'error': f'Portfolio LLM analysis failed: {str(e)}'}), 500


def build_comparative_tables(stocks_data, selected_analysts):
    """Build clean, professional comparative tables optimized for demo presentation"""
    tables = ""

    # Fundamentals Table - Clean and Professional
    if any(s['fundamentals'] for s in stocks_data.values()):
        tables += "## 📊 Fundamental Comparison\n\n"
        tables += "| Metric | " + " | ".join(stocks_data.keys()) + " |\n"
        tables += "|" + "|".join([":---"] + [":---:"] * len(stocks_data)) + "|\n"

        # Key metrics only - most important for investment decisions
        first_stock = next((s for s in stocks_data.values() if s['fundamentals']), None)
        if first_stock and first_stock['fundamentals']:
            # Most critical metrics for comparison
            metrics = [
                ('market_cap', 'Market Cap', 'B'),
                ('revenue', 'Revenue', 'B'),
                ('net_income', 'Net Income', 'B'),
                ('eps', 'EPS', '$'),
                ('pe_ratio', 'P/E Ratio', 'x'),
                ('profit_margin', 'Profit Margin', '%'),
                ('roe', 'ROE', '%'),
                ('debt_to_equity', 'Debt/Equity', 'x'),
                ('revenue_growth', 'Revenue Growth', '%')
            ]

            for metric_key, metric_name, unit in metrics:
                row = f"| **{metric_name}** |"
                for ticker, data in stocks_data.items():
                    if data['fundamentals'] and metric_key in data['fundamentals']:
                        value = data['fundamentals'][metric_key]
                        if value is not None:
                            if unit == 'B':
                                row += f" ${value/1e9:.2f}B |"
                            elif unit == '%':
                                row += f" {value:.1f}% |"
                            elif unit == 'x':
                                row += f" {value:.2f}x |"
                            elif unit == '$':
                                row += f" ${value:.2f} |"
                        else:
                            row += " N/A |"
                    else:
                        row += " N/A |"
                tables += row + "\n"
        tables += "\n"

    # Technical Table - Clean and Professional
    if any(s['technical'] for s in stocks_data.values()):
        tables += "## 📈 Technical Comparison\n\n"
        tables += "| Indicator | " + " | ".join(stocks_data.keys()) + " |\n"
        tables += "|" + "|".join([":---"] + [":---:"] * len(stocks_data)) + "|\n"

        # Key technical indicators
        indicators = [
            ('current_price', 'Current Price', '$'),
            ('sma_20', '20-Day SMA', '$'),
            ('sma_50', '50-Day SMA', '$'),
            ('sma_200', '200-Day SMA', '$'),
            ('rsi', 'RSI', ''),
            ('macd', 'MACD', ''),
            ('volatility', 'Volatility', '%'),
            ('atr', 'ATR', '$')
        ]

        for indicator_key, indicator_name, unit in indicators:
            row = f"| **{indicator_name}** |"
            for ticker, data in stocks_data.items():
                if data['technical'] and indicator_key in data['technical']:
                    value = data['technical'][indicator_key]
                    if value is not None:
                        if unit == '$':
                            row += f" ${value:.2f} |"
                        elif unit == '%':
                            row += f" {value:.1f}% |"
                        else:
                            row += f" {value:.2f} |"
                    else:
                        row += " N/A |"
                else:
                    row += " N/A |"
            tables += row + "\n"
        tables += "\n"

    # Sentiment Table - Clean and Professional
    if any(s['sentiment'] for s in stocks_data.values()):
        tables += "## 📰 Sentiment Comparison\n\n"
        tables += "| Metric | " + " | ".join(stocks_data.keys()) + " |\n"
        tables += "|" + "|".join([":---"] + [":---:"] * len(stocks_data)) + "|\n"

        sent_metrics = [
            ('overall_sentiment', 'Overall Sentiment'),
            ('sentiment_strength', 'Sentiment Strength'),
            ('bullish_count', 'Bullish News'),
            ('bearish_count', 'Bearish News'),
            ('news_count', 'Total News')
        ]

        for metric_key, metric_name in sent_metrics:
            row = f"| **{metric_name}** |"
            for ticker, data in stocks_data.items():
                if data['sentiment'] and metric_key in data['sentiment']:
                    value = data['sentiment'][metric_key]
                    row += f" {value} |"
                else:
                    row += " N/A |"
            tables += row + "\n"
        tables += "\n"

    return tables


def generate_llm_portfolio_recommendation(stocks_data, comparative_tables, trade_date):
    """Use LLM to generate portfolio recommendation based on available data"""
    from ibm_watsonx_ai.foundation_models import ModelInference

    # Prepare data summary for LLM
    tickers_list = list(stocks_data.keys())
    data_types_available = []
    if any(s['fundamentals'] for s in stocks_data.values()):
        data_types_available.append("fundamental analysis")
    if any(s['technical'] for s in stocks_data.values()):
        data_types_available.append("technical analysis")
    if any(s['sentiment'] for s in stocks_data.values()):
        data_types_available.append("sentiment analysis")

    prompt = f"""You are a professional portfolio manager analyzing {len(tickers_list)} stocks: {', '.join(tickers_list)}

Analysis Date: {trade_date}

{comparative_tables}

## Task: Generate Portfolio Analysis & Allocation

Based on the comparative data above, provide:

### 1. Stock Rankings & Grades
For EACH stock, provide:
- **Grade** (A/B/C)
- **Key Strengths** (1-2 sentences citing specific metrics from tables)
- **Key Weaknesses** (1 sentence)

### 2. Portfolio Allocation
| Stock | Allocation % | Rationale |
|-------|--------------|-----------|
| TICKER | XX% | 1-2 sentence justification based on data |

**Total must equal 100%**

### 3. Strategy & Risk
- **Investment Strategy**: Growth/Value/Balanced - explain why based on comparative metrics
- **Key Risks**: Top 2-3 portfolio-level risks
- **Expected Return (12-month)**: Best/Base/Worst case with %

### 4. Actionable Recommendations
- **Entry Timing**: When to enter positions
- **Position Sizing**: All-in or phased entry?
- **Exit Signals**: What metrics indicate it's time to sell

**Requirements**:
- Reference SPECIFIC numbers from the tables above
- Keep analysis concise and data-driven
- No generic statements - cite actual metrics
- Write in ENGLISH only

Generate the analysis now:"""

    # Call WatsonX LLM
    from ibm_watsonx_ai import Credentials

    credentials = Credentials(
        url=WATSONX_CONFIG["watsonx_url"],
        api_key=WATSONX_CONFIG["watsonx_api_key"]
    )

    model = ModelInference(
        model_id=WATSONX_CONFIG["deep_think_llm"],
        credentials=credentials,
        project_id=WATSONX_CONFIG["watsonx_project_id"],
        params={
            "max_new_tokens": 6000,  # Concise, professional output
            "temperature": 0.3,
            "top_p": 0.9,
        }
    )

    print("[PORTFOLIO_LLM] Calling WatsonX for recommendation...", flush=True)
    response = model.generate_text(prompt=prompt)

    # Build clean, professional report
    report = f"""# 📊 Portfolio Analysis Report

**Date**: {trade_date}
**Stocks**: {', '.join(tickers_list)}

---

{comparative_tables}

---

# 💼 Portfolio Recommendation

{response}

---

*Generated by AI Trading Analysis System | Powered by IBM WatsonX AI*
"""

    return report


def handle_portfolio_optimization():
    """Run portfolio optimization after all stocks analyzed"""
    global portfolio_mode, portfolio_tickers, portfolio_results, portfolio_trade_date, waiting_for, selected_analysts_choice

    print(f"[PORTFOLIO] Running portfolio optimization for {len(portfolio_results)} stocks...", flush=True)

    try:
        # Import portfolio components
        from tradingagents.portfolio.stock_data_aggregator import StockDataAggregator
        from tradingagents.portfolio.multi_scenario_portfolio_optimizer import MultiScenarioPortfolioOptimizer
        from tradingagents.portfolio.portfolio_report_generator import PortfolioReportGenerator

        # Check if we have enough stocks
        if len(portfolio_results) < 2:
            waiting_for = None
            portfolio_mode = False
            return jsonify({
                'response': f"⚠️ Portfolio optimization requires at least 2 stocks with complete data. Only {len(portfolio_results)} stock(s) analyzed.",
                'waiting_for': None
            })

        # Get ticker list from results
        completed_tickers = list(portfolio_results.keys())
        print(f"[PORTFOLIO] Completed tickers: {completed_tickers}", flush=True)
        print(f"[PORTFOLIO] Selected analysts: {selected_analysts_choice}", flush=True)

        # Step 1: Aggregate stock data from CSV files
        aggregator = StockDataAggregator(portfolio_trade_date)

        try:
            aggregated_result = aggregator.aggregate_multiple_stocks(completed_tickers)
        except Exception as e:
            error_msg = str(e)
            print(f"[PORTFOLIO] Error aggregating stock data: {error_msg}", flush=True)

            # If error is due to missing data (e.g., 'risk_metrics'), use LLM fallback
            if "'risk_metrics'" in error_msg or "'metrics'" in error_msg or "KeyError" in str(type(e).__name__):
                print(f"[PORTFOLIO] Missing data detected. Using LLM fallback for partial analyst data...", flush=True)
                return handle_portfolio_llm_fallback(completed_tickers)

            waiting_for = None
            portfolio_mode = False
            return jsonify({
                'response': f"⚠️ Error loading stock data for portfolio optimization.\n\nError: {error_msg}",
                'waiting_for': None
            })

        if aggregated_result['num_stocks'] < 2:
            waiting_for = None
            portfolio_mode = False
            return jsonify({
                'response': f"⚠️ Portfolio optimization requires at least 2 stocks with complete CSV data. Found {aggregated_result['num_stocks']} stock(s).",
                'waiting_for': None
            })

        # Step 2: Get returns data for optimization
        print("[PORTFOLIO] Fetching historical price data for optimization...", flush=True)
        returns_data = {}
        for ticker in aggregated_result['stocks_data'].keys():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="3mo")  # CHANGED: 3 months instead of 6 for faster loading
                if not hist.empty:
                    returns_data[ticker] = hist['Close'].pct_change().dropna()
                    print(f"[PORTFOLIO] Fetched {len(returns_data[ticker])} returns for {ticker}", flush=True)
            except Exception as e:
                print(f"[PORTFOLIO] Error fetching {ticker}: {e}", flush=True)

        if len(returns_data) < 2:
            waiting_for = None
            portfolio_mode = False
            return jsonify({
                'response': "⚠️ Could not fetch price data for portfolio optimization.",
                'waiting_for': None
            })

        returns_df = pd.DataFrame(returns_data).dropna()
        print(f"[PORTFOLIO] Combined returns dataframe shape: {returns_df.shape}", flush=True)

        # Step 3: Run optimization
        print("[PORTFOLIO] Running multi-scenario optimization...", flush=True)
        stock_metrics = {ticker: data['metrics'] for ticker, data in aggregated_result['stocks_data'].items()}
        optimizer = MultiScenarioPortfolioOptimizer(returns_df, stock_metrics)
        optimization_scenarios = optimizer.optimize_all_scenarios()
        print(f"[PORTFOLIO] Generated {len(optimization_scenarios)} optimization scenarios", flush=True)

        # Step 4: Generate portfolio report
        print("[PORTFOLIO] Generating comprehensive portfolio report...", flush=True)
        report_generator = PortfolioReportGenerator(
            aggregated_result,
            optimization_scenarios,
            portfolio_trade_date
        )
        report_path = report_generator.generate_comprehensive_report()
        print(f"[PORTFOLIO] Report saved to: {report_path}", flush=True)

        # Step 5: Extract portfolio recommendation from report
        with open(report_path, 'r', encoding='utf-8') as f:
            portfolio_report = f.read()

        # Reset portfolio mode
        portfolio_mode = False
        completed_stocks_list = ', '.join(completed_tickers)
        num_scenarios = len(optimization_scenarios)

        # Build summary with COMPLETE report (no truncation)
        summary_text = f"""✅ **PORTFOLIO ANALYSIS COMPLETE**

**Analyzed Stocks**: {completed_stocks_list} ({len(completed_tickers)} stocks)

**Multi-Scenario Optimization Results:**
- Generated {num_scenarios} optimization scenarios
- Optimization methods: Max Sharpe, Min Variance, Risk Parity, Max Diversification, HRP

**Report Location:** `{report_path}`

---

## Complete Portfolio Report

{portfolio_report}

---

**📄 Full portfolio report saved to:** `{report_path}`

Portfolio analysis complete! You can start a new analysis by typing 'start over' or refreshing the page.
"""

        waiting_for = None

        return jsonify({
            'response': summary_text,
            'waiting_for': None
        })

    except Exception as e:
        print(f"[ERROR] Portfolio optimization failed: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        waiting_for = None
        portfolio_mode = False
        return jsonify({'error': f'Portfolio optimization failed: {str(e)}'}), 500


@app.route('/api/charts/<path:filepath>')
def serve_chart(filepath):
    """Serve chart images from results directory"""
    try:
        # Security: only allow serving from results directory
        results_dir = os.path.join(project_root, 'results')
        return send_from_directory(results_dir, filepath)
    except Exception as e:
        print(f"[ERROR] Failed to serve chart {filepath}: {str(e)}", flush=True)
        return jsonify({'error': 'Chart not found'}), 404


if __name__ == '__main__':
    print("=" * 70)
    print("AI Trading Analysis - Flask Chat Interface")
    print("=" * 70)
    print()
    print("[OK] WatsonX configuration loaded")
    print(f"[MODEL] {WATSONX_CONFIG['deep_think_llm']}")
    print()
    print("[INFO] Starting Flask server...")
    print("[INFO] Open your browser to: http://localhost:7862")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    app.run(host='0.0.0.0', port=7862, debug=False)
