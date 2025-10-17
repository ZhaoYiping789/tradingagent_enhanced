"""
Simple Chat-based Interactive UI

A ChatGPT-style interface for interactive trading analysis.
"""

import gradio as gr
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import time

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from .interactive_workflow import InteractiveWorkflowController
from .user_preference_parser import create_preference_parser
from .feedback_analyzer import create_feedback_analyzer, FeedbackAction


class SimpleChatUI:
    """Simple chat-based UI for trading analysis"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize UI"""
        self.config = config or DEFAULT_CONFIG.copy()

        # Initialize components
        self.graph = None
        self.controller = None
        self.preference_parser = None
        self.feedback_analyzer = None

        # Chat state
        self.chat_history = []
        self.waiting_for = None  # 'initial_setup', 'feedback', None
        self.current_analyst = None

    def _initialize_components(self):
        """Initialize graph and workflow controller"""
        if not self.graph:
            self.graph = TradingAgentsGraph(
                selected_analysts=["market"],
                debug=False,
                config=self.config
            )

            llm = self.graph.quick_thinking_llm

            self.preference_parser = create_preference_parser(llm)
            self.feedback_analyzer = create_feedback_analyzer(llm)

            self.controller = InteractiveWorkflowController(
                graph=self.graph,
                preference_parser=self.preference_parser,
                feedback_analyzer=self.feedback_analyzer,
                ui_callback=None
            )

    def chat(self, message: str, history):
        """
        Process user message

        Args:
            message: User's message
            history: Chat history

        Returns:
            Updated history
        """
        if not message.strip():
            return history

        # Add user message to history
        if history is None:
            history = []
        history.append([message, None])

        # Process based on current state
        if self.waiting_for == 'initial_setup':
            # User provided ticker and preferences
            response = self._handle_initial_setup(message)

        elif self.waiting_for == 'feedback':
            # User provided feedback on analyst
            response = self._handle_feedback(message)

        else:
            # Initial state - ask for setup
            response = self._ask_for_setup()

        # Update last response
        history[-1][1] = response

        return history

    def _ask_for_setup(self):
        """Ask user for initial setup"""
        self.waiting_for = 'initial_setup'
        return """👋 Welcome to AI Trading Analysis!

I'll help you analyze stocks using specialized AI analysts.

**To get started, please tell me:**
1. **Stock ticker** (e.g., NVDA, AAPL)
2. **Your preferences** (optional - e.g., "I'm risk-averse, focus on fundamentals")

Example: "Analyze NVDA. I care about long-term growth and profitability."
"""

    def _handle_initial_setup(self, message: str):
        """Handle initial setup from user message"""
        try:
            self._initialize_components()

            # Parse ticker from message (simple approach - look for capitalized 3-5 letter words)
            import re
            ticker_match = re.search(r'\b([A-Z]{1,5})\b', message)
            if not ticker_match:
                return "❌ I couldn't find a stock ticker. Please include it in CAPS (e.g., NVDA, AAPL)"

            ticker = ticker_match.group(1)

            # Use current date
            trade_date = datetime.now().strftime("%Y-%m-%d")

            # Select analysts (start with just market analyst)
            selected_analysts = ["market", "fundamentals", "news"]

            # Initialize workflow
            self.controller.initialize(
                company_of_interest=ticker,
                trade_date=trade_date,
                selected_analysts=selected_analysts,
                user_preference_text=message
            )

            # Get preferences summary
            prefs = self.controller.workflow_state.user_preferences
            prefs_text = ""
            if prefs and (prefs.focus_areas or prefs.principles):
                prefs_text = "\n\n**Your preferences:**\n"
                if prefs.focus_areas:
                    prefs_text += f"- Focus: {', '.join(prefs.focus_areas)}\n"
                if prefs.risk_tolerance:
                    prefs_text += f"- Risk tolerance: {prefs.risk_tolerance}\n"

            # Start first analyst
            response = f"""✅ **Analysis started for {ticker}**{prefs_text}

📊 Running Market/Technical Analyst...
"""

            # Run first analyst
            self.waiting_for = None
            result = self.controller.run_current_analyst()

            if "error" in result:
                return f"❌ Error: {result['error']}"

            # Display analyst result
            self.current_analyst = result['analyst']
            analyst_response = f"""

---

## 📊 Market/Technical Analyst Report

{result['report']}

---

**What would you like to do?**

Type:
- **"approved"** or **"ok"** to continue to next analyst
- **Specific feedback** to request revision (e.g., "Focus more on RSI indicators")
"""

            self.waiting_for = 'feedback'

            return response + analyst_response

        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"❌ Error: {str(e)}"

    def _handle_feedback(self, message: str):
        """Handle user feedback on current analyst"""
        try:
            # Process feedback
            analysis = self.controller.process_feedback(message)

            if analysis.action == FeedbackAction.APPROVE:
                # Move to next analyst
                if self.controller.workflow_state.is_complete():
                    # All done - generate final decision
                    final = self.controller.get_final_decision()
                    self.waiting_for = None
                    return f"""✅ **All analysts completed!**

---

{final}

---

Analysis complete! Start a new analysis anytime by sending a new ticker."""

                else:
                    # Run next analyst
                    next_analyst = self.controller.workflow_state.get_current_analyst()
                    analyst_names = {
                        "market": "📊 Market/Technical",
                        "fundamentals": "💰 Fundamentals",
                        "news": "📰 News",
                        "social": "🗣️ Social Media"
                    }

                    response = f"""✅ Approved! Moving to next analyst...

{analyst_names.get(next_analyst, next_analyst)} Analyst running...
"""

                    # Run next analyst
                    result = self.controller.run_current_analyst()

                    if "error" in result:
                        return f"❌ Error: {result['error']}"

                    self.current_analyst = result['analyst']

                    analyst_response = f"""

---

## {analyst_names.get(self.current_analyst, self.current_analyst)} Analyst Report

{result['report']}

---

**What would you like to do?**

Type:
- **"approved"** or **"ok"** to continue
- **Specific feedback** to request revision
"""

                    return response + analyst_response

            elif analysis.needs_revision():
                # Rerun with feedback
                response = f"""🔄 **Revision requested**

Revision instructions: {analysis.revision_instructions}

Re-running {self.current_analyst} analyst...
"""

                # Rerun current analyst
                result = self.controller.run_current_analyst()

                if "error" in result:
                    return f"❌ Error: {result['error']}"

                analyst_response = f"""

---

## {self.current_analyst.title()} Analyst Report (Revised)

{result['report']}

---

**What would you like to do?**

Type:
- **"approved"** or **"ok"** to continue
- **More feedback** for another revision
"""

                return response + analyst_response

            else:
                # Need clarification
                return f"""❓ **Need clarification**

{', '.join(analysis.questions)}

Please provide more specific feedback."""

        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"❌ Error: {str(e)}"


def create_simple_ui(config: Optional[Dict[str, Any]] = None):
    """Create simple chat UI"""

    ui = SimpleChatUI(config)

    with gr.Blocks(title="AI Trading Analysis", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🤖 AI Trading Analysis Assistant
        ### Chat-based Interactive Stock Analysis

        Have a conversation with AI analysts to get comprehensive trading insights.
        """)

        chatbot = gr.Chatbot(
            height=600,
            show_label=False
        )

        with gr.Row():
            msg = gr.Textbox(
                placeholder="Type your message here...",
                show_label=False,
                scale=9
            )
            submit = gr.Button("Send", scale=1, variant="primary")

        # Auto-trigger welcome message on load
        def initial_greeting():
            return [[None, ui._ask_for_setup()]]

        # Handle message submission
        def respond(message, chat_history):
            return ui.chat(message, chat_history)

        # Wire up events
        app.load(initial_greeting, outputs=[chatbot])

        msg.submit(respond, [msg, chatbot], [chatbot]).then(
            lambda: "", None, [msg]
        )
        submit.click(respond, [msg, chatbot], [chatbot]).then(
            lambda: "", None, [msg]
        )

    return app


def launch_simple_ui(config: Optional[Dict[str, Any]] = None, **kwargs):
    """Launch simple chat UI"""
    app = create_simple_ui(config)

    launch_kwargs = {
        "server_name": "0.0.0.0",
        "server_port": 7862,
        "share": False,
        "show_error": True
    }
    launch_kwargs.update(kwargs)

    app.launch(**launch_kwargs)


if __name__ == "__main__":
    # Test with default config
    launch_simple_ui()
