"""
Gradio UI for Interactive Trading Analysis

Provides a user-friendly web interface for interactive stock analysis.
"""

import gradio as gr
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import json

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from .interactive_workflow import InteractiveWorkflowController, WorkflowStage
from .user_preference_parser import create_preference_parser
from .feedback_analyzer import create_feedback_analyzer, FeedbackAction


class TradingAnalysisUI:
    """Gradio UI for interactive trading analysis"""

    AVAILABLE_ANALYSTS = {
        "market": "📊 Market/Technical Analyst (RSI, MACD, Bollinger Bands)",
        "fundamentals": "💰 Fundamentals Analyst (P/E, Revenue, Cash Flow)",
        "news": "📰 News Analyst (Sentiment & Impact)",
        "social": "🗣️ Social Media Analyst (Reddit/Twitter)",
        "comprehensive_quantitative": "🔬 Quantitative Analyst (ML Forecasting)",
        "portfolio": "📈 Portfolio Analyst (Correlation & Diversification)",
        "enterprise_strategy": "🏢 Enterprise Strategy Analyst"
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize UI

        Args:
            config: Configuration dictionary (uses DEFAULT_CONFIG if None)
        """
        self.config = config or DEFAULT_CONFIG.copy()

        # Initialize components
        self.graph = None
        self.controller = None
        self.preference_parser = None
        self.feedback_analyzer = None

        # State tracking
        self.current_state = {
            "initialized": False,
            "current_analyst_report": "",
            "analysis_history": []
        }

    def _initialize_components(self):
        """Initialize graph and workflow controller"""
        if not self.graph:
            # Create graph with explicit config parameter
            self.graph = TradingAgentsGraph(
                selected_analysts=["market"],  # Will be overridden later
                debug=False,
                config=self.config
            )

            # Create LLM for parsing (use quick_think_llm for efficiency)
            llm = self.graph.quick_thinking_llm  # Use graph's LLM

            # Create parsers
            self.preference_parser = create_preference_parser(llm)
            self.feedback_analyzer = create_feedback_analyzer(llm)

            # Create controller
            self.controller = InteractiveWorkflowController(
                graph=self.graph,
                preference_parser=self.preference_parser,
                feedback_analyzer=self.feedback_analyzer,
                ui_callback=self._handle_workflow_update
            )

    def _handle_workflow_update(self, update: Dict[str, Any]):
        """Handle updates from workflow controller"""
        print(f"Workflow update: {update.get('message', '')}")

    def start_analysis(
        self,
        ticker: str,
        date: str,
        selected_analysts: List[str],
        preferences: str
    ) -> Tuple[str, str, str]:
        """
        Start the analysis workflow

        Returns:
            (status_message, preferences_summary, next_step_instructions)
        """
        try:
            self._initialize_components()

            # Validate inputs
            if not ticker:
                return "❌ Error: Please enter a stock ticker", "", ""

            if not selected_analysts:
                return "❌ Error: Please select at least one analyst", "", ""

            # Initialize workflow
            self.controller.initialize(
                company_of_interest=ticker.upper(),
                trade_date=date or datetime.now().strftime("%Y-%m-%d"),
                selected_analysts=selected_analysts,
                user_preference_text=preferences
            )

            # Get preferences summary
            user_prefs = self.controller.workflow_state.user_preferences
            prefs_summary = self._format_preferences(user_prefs)

            self.current_state["initialized"] = True

            status = f"✅ Analysis initialized for **{ticker.upper()}**\n\n"
            status += f"📅 Date: {date}\n"
            status += f"👥 Analysts: {', '.join(selected_analysts)}\n\n"
            status += "Click **Run Next Analyst** to begin!"

            next_step = "Click the **Run Next Analyst** button below to start the analysis."

            return status, prefs_summary, next_step

        except Exception as e:
            return f"❌ Error: {str(e)}", "", ""

    def run_next_analyst(self) -> Tuple[str, str, str, bool, bool]:
        """
        Run the next analyst in the sequence

        Returns:
            (analyst_name, report, status, show_feedback, show_next_button)
        """
        if not self.current_state["initialized"]:
            return "Not initialized", "❌ Please initialize analysis first", "Error", False, False

        try:
            # Check if complete
            if self.controller.workflow_state.is_complete():
                return "Complete", "✅ All analysts have completed!", "Ready for final decision", False, False

            # Get current analyst
            current_analyst = self.controller.workflow_state.get_current_analyst()

            # Run analyst
            result = self.controller.run_current_analyst()

            if "error" in result:
                return current_analyst, f"❌ Error: {result['error']}", "Error", False, True

            # Store report
            self.current_state["current_analyst_report"] = result["report"]
            self.current_state["analysis_history"].append({
                "analyst": current_analyst,
                "report": result["report"],
                "timestamp": datetime.now().isoformat()
            })

            # Format report
            analyst_name = self.AVAILABLE_ANALYSTS.get(current_analyst, current_analyst)
            report_display = f"# {analyst_name}\n\n{result['report']}"

            status = f"✅ {current_analyst} completed in {result.get('duration', 0):.1f}s"

            # Show feedback UI
            return analyst_name, report_display, status, True, False

        except Exception as e:
            return "Error", f"❌ Exception: {str(e)}", "Error", False, True

    def process_user_feedback(self, feedback_text: str) -> Tuple[str, bool, bool]:
        """
        Process user feedback on current analyst

        Returns:
            (feedback_analysis, show_next_button, show_rerun_button)
        """
        if not feedback_text:
            feedback_text = "approved"  # Default to approval

        try:
            # Process feedback
            analysis = self.controller.process_feedback(feedback_text)

            # Format analysis
            result_text = f"**Feedback Analysis**\n\n"
            result_text += f"- **Action**: {analysis.action.value.upper()}\n"

            if analysis.action == FeedbackAction.APPROVE:
                result_text += f"- **Result**: ✅ Approved! Moving to next analyst.\n"
                return result_text, True, False  # Show next button

            elif analysis.needs_revision():
                result_text += f"- **Result**: 🔄 Revision requested\n"
                result_text += f"- **Focus Points**: {', '.join(analysis.focus_points)}\n"
                result_text += f"- **Instructions**: {analysis.revision_instructions}\n"
                return result_text, False, True  # Show rerun button

            else:  # CLARIFY
                result_text += f"- **Questions**: {', '.join(analysis.questions)}\n"
                result_text += "Please provide more specific feedback."
                return result_text, False, False

        except Exception as e:
            return f"❌ Error processing feedback: {str(e)}", False, False

    def get_final_decision(self) -> str:
        """Get final trading decision"""
        try:
            final_report = self.controller.get_final_decision()
            return final_report
        except Exception as e:
            return f"❌ Error generating final decision: {str(e)}"

    def _format_preferences(self, prefs) -> str:
        """Format user preferences for display"""
        if not prefs:
            return "No specific preferences provided"

        parts = ["## Your Preferences\n"]

        if prefs.focus_areas:
            parts.append(f"**📊 Focus Areas**: {', '.join(prefs.focus_areas)}")

        if prefs.principles:
            parts.append(f"**📋 Principles**: {', '.join(prefs.principles)}")

        if prefs.constraints:
            parts.append(f"**⚠️ Constraints**: {', '.join(prefs.constraints)}")

        parts.append(f"**🎯 Risk Tolerance**: {prefs.risk_tolerance}")
        parts.append(f"**⏰ Investment Horizon**: {prefs.investment_horizon}")

        if prefs.custom_instructions:
            parts.append(f"\n**💡 Custom Instructions**:\n{prefs.custom_instructions}")

        return "\n\n".join(parts)

    def get_progress_info(self) -> str:
        """Get current progress information"""
        if not self.controller:
            return "Not started"

        state = self.controller.get_state_summary()
        progress = state.get("progress", 0)
        current = state.get("current_analyst", "None")

        return f"**Progress**: {progress:.0f}% | **Current**: {current}"

    def create_ui(self) -> gr.Blocks:
        """Create and return the Gradio interface"""

        with gr.Blocks(title="Trading Analysis Assistant", theme=gr.themes.Soft()) as app:
            gr.Markdown("""
            # 🤖 AI-Powered Trading Analysis Assistant
            ### Interactive Multi-Agent Stock Analysis System (WatsonX Edition)

            This system uses specialized AI analysts to provide comprehensive trading insights.
            You can guide the analysis with your preferences and review each analyst's work.
            """)

            with gr.Tabs() as tabs:
                # Tab 1: Setup
                with gr.Tab("1️⃣ Setup & Preferences"):
                    gr.Markdown("### Configure Your Analysis")

                    with gr.Row():
                        with gr.Column(scale=1):
                            ticker_input = gr.Textbox(
                                label="Stock Ticker",
                                placeholder="e.g., NVDA, AAPL, MSFT",
                                value="NVDA"
                            )

                            date_input = gr.Textbox(
                                label="Analysis Date (YYYY-MM-DD)",
                                placeholder="Leave blank for today",
                                value=datetime.now().strftime("%Y-%m-%d")
                            )

                        with gr.Column(scale=2):
                            analyst_selector = gr.CheckboxGroup(
                                choices=list(self.AVAILABLE_ANALYSTS.values()),
                                label="Select Analysts",
                                value=[
                                    self.AVAILABLE_ANALYSTS["market"],
                                    self.AVAILABLE_ANALYSTS["fundamentals"],
                                    self.AVAILABLE_ANALYSTS["news"]
                                ]
                            )

                    gr.Markdown("### Your Analysis Preferences (Optional)")
                    gr.Markdown("Tell the analysts what you care about, what principles to follow, or what to avoid.")

                    preferences_input = gr.Textbox(
                        label="Your Preferences & Requirements",
                        placeholder="Example: I'm risk-averse and care most about profitability and cash flow. Don't rely too heavily on technical indicators. Focus on long-term fundamentals.",
                        lines=5
                    )

                    start_button = gr.Button("🚀 Start Analysis", variant="primary", size="lg")

                    with gr.Accordion("Preferences Summary", open=False):
                        preferences_display = gr.Markdown("No preferences set yet")

                    status_display = gr.Markdown("")

                # Tab 2: Analysis Progress
                with gr.Tab("2️⃣ Analysis & Review"):
                    gr.Markdown("### Review Each Analyst's Work")

                    progress_bar = gr.Markdown("**Progress**: 0%")

                    with gr.Row():
                        next_analyst_button = gr.Button(
                            "▶️ Run Next Analyst",
                            variant="primary",
                            visible=True
                        )

                    analyst_name_display = gr.Markdown("### No analyst running yet")
                    analyst_report_display = gr.Markdown("")

                    analyst_status = gr.Markdown("")

                    gr.Markdown("---")
                    gr.Markdown("### Your Feedback")
                    gr.Markdown("Review the analysis above. Approve to continue, or provide feedback for revision.")

                    feedback_input = gr.Textbox(
                        label="Your Feedback",
                        placeholder="Type 'ok' or 'approved' to continue, or provide specific feedback...",
                        lines=3,
                        visible=False
                    )

                    with gr.Row():
                        submit_feedback_button = gr.Button(
                            "✅ Submit Feedback",
                            variant="primary",
                            visible=False
                        )

                        rerun_analyst_button = gr.Button(
                            "🔄 Rerun with Feedback",
                            variant="secondary",
                            visible=False
                        )

                    feedback_analysis_display = gr.Markdown("")

                # Tab 3: Final Decision
                with gr.Tab("3️⃣ Final Decision"):
                    gr.Markdown("### Comprehensive Trading Decision")

                    generate_final_button = gr.Button(
                        "📊 Generate Final Decision",
                        variant="primary",
                        size="lg"
                    )

                    final_decision_display = gr.Markdown("Complete all analyst reviews to see final decision")

                    with gr.Accordion("Analysis History", open=False):
                        history_display = gr.JSON(label="All Analyst Reports")

            # Event handlers
            def start_analysis_handler(ticker, date, analysts_display, prefs):
                # Map display names back to analyst codes
                analyst_codes = []
                for code, display in self.AVAILABLE_ANALYSTS.items():
                    if display in analysts_display:
                        analyst_codes.append(code)

                status, prefs_summary, next_step = self.start_analysis(
                    ticker, date, analyst_codes, prefs
                )
                return status, prefs_summary

            def run_analyst_handler():
                name, report, status, show_feedback, show_next = self.run_next_analyst()
                progress = self.get_progress_info()

                return (
                    f"### {name}",  # analyst_name_display
                    report,  # analyst_report_display
                    status,  # analyst_status
                    progress,  # progress_bar
                    gr.update(visible=show_feedback),  # feedback_input
                    gr.update(visible=show_feedback),  # submit_feedback_button
                    gr.update(visible=show_next)  # next_analyst_button
                )

            def feedback_handler(feedback):
                result, show_next, show_rerun = self.process_user_feedback(feedback)

                return (
                    result,  # feedback_analysis_display
                    gr.update(visible=show_next),  # next_analyst_button
                    gr.update(visible=show_rerun),  # rerun_analyst_button
                    gr.update(visible=False),  # feedback_input
                    gr.update(visible=False)  # submit_feedback_button
                )

            def final_decision_handler():
                final = self.get_final_decision()
                history = self.current_state.get("analysis_history", [])
                return final, history

            # Wire up events
            start_button.click(
                fn=start_analysis_handler,
                inputs=[ticker_input, date_input, analyst_selector, preferences_input],
                outputs=[status_display, preferences_display]
            )

            next_analyst_button.click(
                fn=run_analyst_handler,
                outputs=[
                    analyst_name_display,
                    analyst_report_display,
                    analyst_status,
                    progress_bar,
                    feedback_input,
                    submit_feedback_button,
                    next_analyst_button
                ]
            )

            submit_feedback_button.click(
                fn=feedback_handler,
                inputs=[feedback_input],
                outputs=[
                    feedback_analysis_display,
                    next_analyst_button,
                    rerun_analyst_button,
                    feedback_input,
                    submit_feedback_button
                ]
            )

            rerun_analyst_button.click(
                fn=run_analyst_handler,
                outputs=[
                    analyst_name_display,
                    analyst_report_display,
                    analyst_status,
                    progress_bar,
                    feedback_input,
                    submit_feedback_button,
                    next_analyst_button
                ]
            )

            generate_final_button.click(
                fn=final_decision_handler,
                outputs=[final_decision_display, history_display]
            )

        return app


def launch_ui(config: Optional[Dict[str, Any]] = None, **kwargs):
    """
    Launch the Gradio UI

    Args:
        config: Configuration dictionary
        **kwargs: Additional arguments for gr.launch() (server_name, server_port, share, etc.)
    """
    ui = TradingAnalysisUI(config)
    app = ui.create_ui()

    # Default launch settings
    launch_kwargs = {
        "server_name": "0.0.0.0",
        "server_port": 7860,
        "share": False,
        "show_error": True
    }
    launch_kwargs.update(kwargs)

    app.launch(**launch_kwargs)


if __name__ == "__main__":
    # For testing
    launch_ui()
