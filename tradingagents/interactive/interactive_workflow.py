"""
Interactive Workflow Controller

Manages the interactive analysis workflow with human-in-the-loop checkpoints.
"""

from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import time

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.agents.utils.agent_states import AgentState
from tradingagents.agents.trader.trader import create_trader
from .user_preference_parser import UserPreferences, UserPreferenceParser
from .feedback_analyzer import FeedbackAnalyzer, FeedbackAnalysis, FeedbackAction
from .graph_executor_helper import GraphExecutorHelper, create_executor_helper


class WorkflowStage(Enum):
    """Stages of the interactive workflow"""
    INITIALIZATION = "initialization"
    PREFERENCE_COLLECTION = "preference_collection"
    ANALYST_EXECUTION = "analyst_execution"
    ANALYST_REVIEW = "analyst_review"
    FINAL_DECISION = "final_decision"
    COMPLETED = "completed"


@dataclass
class AnalystStatus:
    """Status of an individual analyst"""
    analyst_type: str
    status: str  # 'pending', 'running', 'completed', 'needs_revision'
    report: str = ""
    feedback: Optional[FeedbackAnalysis] = None
    revision_count: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    def duration(self) -> Optional[float]:
        """Get execution duration in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


@dataclass
class WorkflowState:
    """Overall state of the interactive workflow"""
    stage: WorkflowStage = WorkflowStage.INITIALIZATION
    company_of_interest: str = ""
    trade_date: str = ""
    selected_analysts: List[str] = field(default_factory=list)
    user_preferences: Optional[UserPreferences] = None

    # Analyst execution tracking
    analyst_statuses: Dict[str, AnalystStatus] = field(default_factory=dict)
    current_analyst_index: int = 0

    # Graph state
    agent_state: Optional[AgentState] = None

    # Final outputs
    final_report: str = ""
    final_decision: str = ""

    def get_current_analyst(self) -> Optional[str]:
        """Get current analyst being processed"""
        if 0 <= self.current_analyst_index < len(self.selected_analysts):
            return self.selected_analysts[self.current_analyst_index]
        return None

    def advance_to_next_analyst(self):
        """Move to next analyst"""
        self.current_analyst_index += 1

    def is_complete(self) -> bool:
        """Check if workflow is complete"""
        return self.current_analyst_index >= len(self.selected_analysts)

    def get_progress_percentage(self) -> float:
        """Get overall progress percentage"""
        if not self.selected_analysts:
            return 0.0
        return (self.current_analyst_index / len(self.selected_analysts)) * 100


class InteractiveWorkflowController:
    """
    Controls the interactive analysis workflow.

    This controller wraps the TradingAgentsGraph and adds human-in-the-loop
    checkpoints after each analyst completes their analysis.
    """

    def __init__(
        self,
        graph: TradingAgentsGraph,
        preference_parser: UserPreferenceParser,
        feedback_analyzer: FeedbackAnalyzer,
        ui_callback: Optional[Callable] = None
    ):
        """
        Initialize controller

        Args:
            graph: The trading agents graph
            preference_parser: Parser for user preferences
            feedback_analyzer: Analyzer for user feedback
            ui_callback: Optional callback for UI updates
        """
        self.graph = graph
        self.preference_parser = preference_parser
        self.feedback_analyzer = feedback_analyzer
        self.ui_callback = ui_callback

        # Create executor helper for running individual analysts
        self.executor = create_executor_helper(graph)

        self.workflow_state = WorkflowState()

    def initialize(
        self,
        company_of_interest: str,
        trade_date: str,
        selected_analysts: List[str],
        user_preference_text: str = ""
    ):
        """
        Initialize the workflow

        Args:
            company_of_interest: Stock ticker
            trade_date: Analysis date
            selected_analysts: List of analyst types to run
            user_preference_text: User's preference input
        """
        self.workflow_state.stage = WorkflowStage.PREFERENCE_COLLECTION
        self.workflow_state.company_of_interest = company_of_interest
        self.workflow_state.trade_date = trade_date
        self.workflow_state.selected_analysts = selected_analysts

        # Parse user preferences
        if user_preference_text:
            self.workflow_state.user_preferences = self.preference_parser.parse(
                user_preference_text
            )
        else:
            # Create default preferences
            self.workflow_state.user_preferences = UserPreferences(
                focus_areas=[],
                principles=[],
                constraints=[],
                risk_tolerance="moderate",
                investment_horizon="medium-term",
                custom_instructions="",
                raw_input=""
            )

        # Initialize analyst statuses
        for analyst in selected_analysts:
            self.workflow_state.analyst_statuses[analyst] = AnalystStatus(
                analyst_type=analyst,
                status="pending"
            )

        # Initialize agent state with user preferences
        self.workflow_state.agent_state = self.executor.create_initial_state(
            company_of_interest=company_of_interest,
            trade_date=trade_date,
            user_preferences=self.workflow_state.user_preferences.to_dict() if self.workflow_state.user_preferences else {}
        )

        self._notify_ui("Workflow initialized")

    def run_current_analyst(self) -> Dict[str, Any]:
        """
        Run the current analyst

        Returns:
            Dict with analyst report and status
        """
        current_analyst = self.workflow_state.get_current_analyst()
        if not current_analyst:
            return {"error": "No analyst to run"}

        self.workflow_state.stage = WorkflowStage.ANALYST_EXECUTION

        analyst_status = self.workflow_state.analyst_statuses[current_analyst]
        analyst_status.status = "running"
        analyst_status.start_time = time.time()

        self._notify_ui(f"Running {current_analyst} analyst...")

        try:
            # Inject user preferences into analyst prompt
            preference_context = ""
            if self.workflow_state.user_preferences:
                preference_context = self.preference_parser.generate_analyst_instructions(
                    self.workflow_state.user_preferences,
                    current_analyst
                )

            # Add revision context if this is a revision
            revision_context = ""
            if analyst_status.revision_count > 0 and analyst_status.feedback:
                # Collect all completed analyst reports for cross-analyst context
                all_completed_reports = {}
                for analyst_type in self.workflow_state.selected_analysts:
                    status = self.workflow_state.analyst_statuses[analyst_type]
                    if status.status == "completed" and status.report:
                        all_completed_reports[analyst_type] = status.report

                revision_context = self.feedback_analyzer.generate_revision_prompt(
                    analyst_status.feedback,
                    analyst_status.report,
                    current_analyst,
                    all_analyst_reports=all_completed_reports
                )

            # Run single analyst through graph
            # We'll use the graph's run method but only for one analyst
            report = self._execute_single_analyst(
                current_analyst,
                preference_context,
                revision_context
            )

            analyst_status.status = "completed"
            analyst_status.report = report
            analyst_status.end_time = time.time()

            self.workflow_state.stage = WorkflowStage.ANALYST_REVIEW

            self._notify_ui(f"{current_analyst} analyst completed")

            return {
                "analyst": current_analyst,
                "report": report,
                "status": "completed",
                "duration": analyst_status.duration()
            }

        except Exception as e:
            analyst_status.status = "error"
            analyst_status.end_time = time.time()
            return {
                "analyst": current_analyst,
                "error": str(e),
                "status": "error"
            }

    def process_feedback(self, feedback_text: str) -> FeedbackAnalysis:
        """
        Process user feedback on current analyst

        Args:
            feedback_text: User's feedback

        Returns:
            FeedbackAnalysis object
        """
        current_analyst = self.workflow_state.get_current_analyst()
        if not current_analyst:
            raise ValueError("No analyst to process feedback for")

        analyst_status = self.workflow_state.analyst_statuses[current_analyst]

        # Collect all completed analyst reports for cross-analyst context
        all_completed_reports = {}
        for analyst_type in self.workflow_state.selected_analysts:
            status = self.workflow_state.analyst_statuses[analyst_type]
            if status.status == "completed" and status.report:
                all_completed_reports[analyst_type] = status.report

        # Analyze feedback with full context
        analysis = self.feedback_analyzer.analyze(
            feedback_text,
            current_analyst,
            analyst_status.report,
            context={
                "preferences": self.workflow_state.user_preferences.to_dict() if self.workflow_state.user_preferences else {},
                "all_analyst_reports": all_completed_reports  # Include all completed reports
            }
        )

        analyst_status.feedback = analysis

        if analysis.needs_revision():
            analyst_status.status = "needs_revision"
            analyst_status.revision_count += 1
            self._notify_ui(f"Revision requested for {current_analyst}")
        elif analysis.action == FeedbackAction.APPROVE:
            # Approved - move to next analyst
            self.workflow_state.advance_to_next_analyst()
            self._notify_ui(f"{current_analyst} approved, moving to next analyst")
        # For CLARIFY or EXPAND actions, don't advance - stay on current analyst for conversation

        return analysis

    def _execute_single_analyst(
        self,
        analyst_type: str,
        preference_context: str,
        revision_context: str
    ) -> str:
        """
        Execute a single analyst node

        Args:
            analyst_type: Type of analyst to run
            preference_context: User preference context
            revision_context: Revision context if applicable

        Returns:
            Analyst report as string
        """
        # Combine preference and revision context
        combined_context = ""
        if preference_context:
            combined_context += preference_context + "\n\n"
        if revision_context:
            combined_context += revision_context + "\n\n"

        # CRITICAL FIX: Clear messages before each analyst to prevent cross-contamination
        # Each analyst should only see their own tool calls, not previous analysts' work
        # This prevents fundamentals analyst from copying market analyst's technical content
        clean_state = dict(self.workflow_state.agent_state)
        clean_state["messages"] = []  # Start fresh for each analyst

        print(f"[DEBUG] Starting {analyst_type} with clean message history", flush=True)

        # Execute the analyst using the executor helper
        report, updated_state = self.executor.execute_analyst_node(
            analyst_type=analyst_type,
            state=clean_state,  # Use clean state, not contaminated state
            user_context=combined_context
        )

        # CRITICAL: MERGE updated_state with existing state, don't replace!
        # Analyst nodes return partial updates (like {messages: [...], market_report: "..."})
        # We must preserve existing fields (company_of_interest, trade_date, etc.)
        for key, value in updated_state.items():
            self.workflow_state.agent_state[key] = value

        # Also ensure the report is in the correct field
        self.workflow_state.agent_state = self.executor.merge_state_with_report(
            self.workflow_state.agent_state,
            analyst_type,
            report
        )

        return report

    def get_final_decision(self) -> str:
        """
        Get final trading decision after all analysts complete

        Returns:
            Final decision report
        """
        if not self.workflow_state.is_complete():
            return "Analysis not complete yet"

        self.workflow_state.stage = WorkflowStage.FINAL_DECISION

        print("[SYNTHESIS] Generating unified analysis from all analyst reports...", flush=True)

        # Aggregate all analyst reports
        all_reports = []
        analyst_names_map = {
            "market": "Market/Technical Analysis",
            "fundamentals": "Fundamental Analysis",
            "news": "News Sentiment Analysis",
            "social": "Social Media Sentiment Analysis",
            "quantitative": "Quantitative Analysis",
            "comprehensive_quantitative": "Comprehensive Quantitative Analysis",
            "portfolio": "Portfolio Analysis",
            "enterprise_strategy": "Enterprise Strategy Analysis"
        }

        for analyst_type in self.workflow_state.selected_analysts:
            status = self.workflow_state.analyst_statuses[analyst_type]
            analyst_name = analyst_names_map.get(analyst_type, analyst_type.title())
            all_reports.append(f"## {analyst_name}\n\n{status.report}\n")

        # Use LLM to synthesize all reports into a unified analysis
        try:
            llm = self.graph.quick_thinking_llm

            synthesis_prompt = f"""You are a senior investment analyst tasked with synthesizing multiple specialist reports into a unified investment recommendation.

**Stock**: {self.workflow_state.company_of_interest}
**Analysis Date**: {self.workflow_state.trade_date}

You have received the following analyst reports:

{''.join(all_reports)}

**Your Task:**
Synthesize these reports into a comprehensive, unified analysis that:

1. **Executive Summary** (2-3 sentences)
   - Provide a clear, concise overview of the investment opportunity

2. **Key Insights by Category**
   - Technical/Market: Summarize price action, trends, momentum, and key indicators
   - Fundamental: Summarize financial health, profitability, growth metrics
   - Sentiment: Summarize news and social media sentiment if available
   - Quantitative: Summarize statistical models and forecasts if available

3. **Convergence and Divergence**
   - Identify where different analyses AGREE (bullish/bearish convergence)
   - Highlight where analyses CONFLICT (e.g., strong technicals but weak fundamentals)
   - Explain what these conflicts mean for the investment decision

4. **Risk Assessment**
   - Key risks identified across all analyses
   - Risk level: Low / Moderate / High
   - Risk mitigation considerations

5. **Final Trading Recommendation**
   - Clear decision: **BUY** / **HOLD** / **SELL**
   - Confidence level: Low / Moderate / High
   - Rationale (2-3 sentences explaining why)
   - Suggested entry points, stop-loss, and price targets if applicable

6. **Key Metrics Summary Table**
   - Create a markdown table with all critical metrics mentioned in reports

**Important Guidelines:**
- Write in clear, professional English
- Be specific - reference actual numbers, percentages, and dates from the reports
- Don't make up information - only use data from the provided reports
- If reports conflict, acknowledge this and explain how you weigh the evidence
- Your recommendation should be actionable and backed by concrete reasoning

**Synthesized Analysis:**"""

            print("[SYNTHESIS] Calling LLM to generate unified report...", flush=True)
            response = llm.invoke(synthesis_prompt)
            synthesized_report = response.content if hasattr(response, 'content') else str(response)
            print(f"[SYNTHESIS] Generated {len(synthesized_report)} character synthesis", flush=True)

            # Generate trading strategy using trader node
            print("[TRADER] Generating detailed trading strategy...", flush=True)
            trading_strategy = ""
            try:
                # Create trader node
                trader_node = create_trader(self.graph.deep_thinking_llm, self.graph.trader_memory)

                # Construct state for trader node
                # Trader needs: company_of_interest, investment_plan, market_report, sentiment_report,
                # news_report, fundamentals_report, quantitative_report, comprehensive_quantitative_report, optimization_results
                trader_state = {
                    "company_of_interest": self.workflow_state.company_of_interest,
                    "investment_plan": synthesized_report,  # Use synthesis as investment plan
                    "market_report": self.workflow_state.agent_state.get("market_report", "No market analysis available"),
                    "sentiment_report": self.workflow_state.agent_state.get("sentiment_report", "No sentiment analysis available"),
                    "news_report": self.workflow_state.agent_state.get("news_report", "No news analysis available"),
                    "fundamentals_report": self.workflow_state.agent_state.get("fundamentals_report", "No fundamental analysis available"),
                    "quantitative_report": self.workflow_state.agent_state.get("quantitative_report", "No quantitative analysis available"),
                    "comprehensive_quantitative_report": self.workflow_state.agent_state.get("comprehensive_quantitative_report", ""),
                    "optimization_results": self.workflow_state.agent_state.get("optimization_results", {})
                }

                # Call trader node
                trader_result = trader_node(trader_state)
                trading_strategy = trader_result.get("trader_investment_plan", "")
                print(f"[TRADER] Generated {len(trading_strategy)} character trading strategy", flush=True)
            except Exception as trader_error:
                print(f"[TRADER] Warning: Failed to generate trading strategy: {str(trader_error)}", flush=True)
                trading_strategy = "Trading strategy generation unavailable. Please review analyst reports for investment insights."

            # Get optimization method info if available
            opt_method_section = ""
            opt_choice = self.workflow_state.agent_state.get('optimization_method_choice', {})
            if opt_choice and 'selected_method' in opt_choice:
                method_names = {
                    'mean_variance': 'Mean-Variance Optimization (Markowitz)',
                    'risk_parity': 'Risk Parity',
                    'min_variance': 'Minimum Variance',
                    'max_sharpe': 'Maximum Sharpe Ratio',
                    'equal_weight': 'Equal Weight'
                }
                opt_method_section = f"""
**Optimization Method Used**: {method_names.get(opt_choice['selected_method'], opt_choice['selected_method'])}
**Risk Tolerance**: {opt_choice.get('risk_tolerance', 'N/A').title()}
"""

            # Create final comprehensive report
            final_report = f"""# COMPREHENSIVE INVESTMENT ANALYSIS

**Stock**: {self.workflow_state.company_of_interest}
**Analysis Date**: {self.workflow_state.trade_date}
**Analysts Consulted**: {', '.join([analyst_names_map.get(a, a.title()) for a in self.workflow_state.selected_analysts])}{opt_method_section}

---

{synthesized_report}

---

## 📊 DETAILED TRADING STRATEGY

{trading_strategy}

---

## Individual Analyst Reports

<details>
<summary>Click to expand detailed analyst reports</summary>

{''.join(all_reports)}

</details>

---

**Analysis Complete** - Generated by AI Trading Analysis System
"""

            self.workflow_state.final_report = final_report
            self.workflow_state.stage = WorkflowStage.COMPLETED

            return final_report

        except Exception as e:
            print(f"[ERROR] Failed to synthesize reports: {str(e)}", flush=True)
            import traceback
            traceback.print_exc()

            # Fallback: return simple concatenation
            fallback_report = f"""
# COMPREHENSIVE ANALYSIS REPORT

**Stock**: {self.workflow_state.company_of_interest}
**Date**: {self.workflow_state.trade_date}

{''.join(all_reports)}

## FINAL DECISION

Note: Automated synthesis failed. Please review individual analyst reports above.
"""
            self.workflow_state.final_report = fallback_report
            self.workflow_state.stage = WorkflowStage.COMPLETED
            return fallback_report

    def _notify_ui(self, message: str):
        """Send notification to UI if callback is set"""
        if self.ui_callback:
            self.ui_callback({
                "type": "notification",
                "message": message,
                "workflow_state": self.workflow_state
            })

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of current workflow state"""
        return {
            "stage": self.workflow_state.stage.value,
            "company": self.workflow_state.company_of_interest,
            "date": self.workflow_state.trade_date,
            "progress": self.workflow_state.get_progress_percentage(),
            "current_analyst": self.workflow_state.get_current_analyst(),
            "analysts": [
                {
                    "type": analyst,
                    "status": status.status,
                    "revision_count": status.revision_count,
                    "duration": status.duration()
                }
                for analyst, status in self.workflow_state.analyst_statuses.items()
            ]
        }
