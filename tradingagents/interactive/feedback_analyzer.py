"""
Feedback Analyzer Module

Analyzes user feedback on analyst reports and determines appropriate actions.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel


class FeedbackAction(Enum):
    """Action to take based on feedback"""
    APPROVE = "approve"  # User approves, proceed to next analyst
    REVISE = "revise"  # Need to revise current analyst's work
    EXPAND = "expand"  # User wants more details on specific aspects
    CLARIFY = "clarify"  # User has questions, need clarification


@dataclass
class FeedbackAnalysis:
    """Structured analysis of user feedback"""

    # Action to take
    action: FeedbackAction

    # Specific aspects user wants changed/expanded
    focus_points: list[str]

    # Questions or concerns raised
    questions: list[str]

    # Additional instructions for re-analysis
    revision_instructions: str

    # Confidence score (0-1)
    confidence: float

    # Original feedback
    raw_feedback: str

    def needs_revision(self) -> bool:
        """Check if revision is needed"""
        return self.action in [FeedbackAction.REVISE, FeedbackAction.EXPAND]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "action": self.action.value,
            "focus_points": self.focus_points,
            "questions": self.questions,
            "revision_instructions": self.revision_instructions,
            "confidence": self.confidence,
            "raw_feedback": self.raw_feedback
        }


class FeedbackAnalyzer:
    """Analyzes user feedback and determines next actions"""

    SYSTEM_PROMPT = """You are an expert analyst assistant that interprets user feedback on financial analysis reports.

You have access to:
1. The CURRENT analyst's full report
2. ALL PREVIOUS analysts' reports (for cross-reference when user mentions data from other analysts)

Your task is to analyze user feedback and determine:
1. **Action**: What should happen next?
   - APPROVE: User is satisfied, proceed to next step
   - REVISE: User wants the analyst to REDO the analysis with a different approach (e.g., "analyze this differently", "redo the analysis focusing on...")
   - CLARIFY: User has questions or needs explanation about content in the report (e.g., "what does X mean?", "explain Y", "why is Z?", "how do X and Y relate?")
   - EXPAND: User wants MORE information or deeper analysis (e.g., "tell me more about...", "give me details on...", "what about...")

**IMPORTANT - Cross-Analyst References**:
- User may reference data from PREVIOUS analysts (e.g., "the first news", "the P/E ratio", "the ATR value")
- When user asks to "combine" or "compare" data across analysts, use CLARIFY action
- Extract the SPECIFIC data points user is referencing from the provided previous reports
- Include these data points in focus_points and questions for proper handling

**Action Guidelines**:
- Use CLARIFY when user asks questions about existing content (what/why/how questions) OR wants to combine/compare data
- Use EXPAND when user requests additional information or deeper dive into current analysis
- Use REVISE ONLY when user explicitly wants to redo the analysis with a different methodology
- When user references "first news", "second indicator", etc., find the specific item in the reports

2. **Focus Points**: Specific aspects user mentioned (metrics, sections, concerns, specific data values)

3. **Questions**: Any explicit or implicit questions user asked

4. **Revision Instructions**: Clear instructions for re-analysis if needed (only for REVISE action)

5. **Confidence**: How confident you are in interpreting the feedback (0.0-1.0)

Return JSON:
{
  "action": "approve|revise|expand|clarify",
  "focus_points": ["specific", "points", "mentioned"],
  "questions": ["user's", "questions"],
  "revision_instructions": "clear instructions for analyst if revision needed",
  "confidence": 0.85
}

Examples of feedback interpretation:
- "Looks good!" -> action: "approve"
- "What does this P/E ratio mean?" -> action: "clarify", questions: ["P/E ratio meaning"]
- "Can you explain how ATR relates to P/E?" -> action: "clarify", questions: ["ATR and P/E relationship"]
- "I need to see the debt-to-equity ratio" -> action: "expand", focus_points: ["debt-to-equity ratio"]
- "Tell me more about cash flow trends" -> action: "expand", focus_points: ["cash flow trends"]
- "Redo this analysis but focus on profitability instead of growth" -> action: "revise", focus_points: ["profitability analysis"]
- "I don't agree with your methodology, use DCF instead" -> action: "revise", focus_points: ["DCF methodology"]
"""

    def __init__(self, llm: BaseChatModel):
        """
        Initialize analyzer

        Args:
            llm: Language model for analysis
        """
        self.llm = llm

    def analyze(
        self,
        feedback: str,
        analyst_type: str,
        analyst_report: str,
        context: Optional[Dict[str, Any]] = None
    ) -> FeedbackAnalysis:
        """
        Analyze user feedback

        Args:
            feedback: User's feedback text
            analyst_type: Type of analyst that generated the report
            analyst_report: The report being reviewed
            context: Additional context (preferences, previous feedback, etc.)

        Returns:
            FeedbackAnalysis object
        """
        # Handle empty feedback (treat as approval)
        if not feedback or feedback.strip().lower() in ["ok", "yes", "y", "next", "continue", "proceed"]:
            return FeedbackAnalysis(
                action=FeedbackAction.APPROVE,
                focus_points=[],
                questions=[],
                revision_instructions="",
                confidence=1.0,
                raw_feedback=feedback
            )

        # Build context message with comprehensive information
        context_parts = [
            f"=== CURRENT ANALYST ===",
            f"Analyst Type: {analyst_type}",
            f"\n=== CURRENT ANALYST'S FULL REPORT ===",
            # Show more of the current report (up to 8000 chars for comprehensive context)
            f"{analyst_report[:8000]}{'...' if len(analyst_report) > 8000 else ''}",
        ]

        # Add all previous analyst reports for cross-reference
        if context and "all_analyst_reports" in context:
            all_reports = context["all_analyst_reports"]
            if all_reports:
                context_parts.append("\n=== PREVIOUS ANALYSTS' REPORTS (for cross-reference) ===")
                context_parts.append("User may reference data from these previous analyses:\n")

                for prev_analyst_type, prev_report in all_reports.items():
                    # Show first 2000 chars of each previous report for context
                    report_preview = prev_report[:2000] if len(prev_report) > 2000 else prev_report
                    context_parts.append(f"\n--- {prev_analyst_type.upper()} ANALYST REPORT ---")
                    context_parts.append(report_preview)
                    if len(prev_report) > 2000:
                        context_parts.append("...")

        # Add user preferences if available
        if context and "preferences" in context and context["preferences"]:
            context_parts.append(f"\n=== USER PREFERENCES ===")
            context_parts.append(json.dumps(context["preferences"], indent=2))

        # Add user feedback at the end
        context_parts.append(f"\n=== USER FEEDBACK ===")
        context_parts.append(feedback)

        # Call LLM
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content="\n".join(context_parts))
        ]

        response = self.llm.invoke(messages)

        # Parse response
        try:
            content = response.content

            # Extract JSON
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            parsed_data = json.loads(json_str)

            # Create FeedbackAnalysis
            action_str = parsed_data.get("action", "approve").lower()
            action = FeedbackAction(action_str)

            analysis = FeedbackAnalysis(
                action=action,
                focus_points=parsed_data.get("focus_points", []),
                questions=parsed_data.get("questions", []),
                revision_instructions=parsed_data.get("revision_instructions", ""),
                confidence=float(parsed_data.get("confidence", 0.8)),
                raw_feedback=feedback
            )

            return analysis

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Warning: Failed to parse feedback analysis: {e}")
            print(f"Response: {response.content}")

            # Default to expand action with feedback as instruction
            return FeedbackAnalysis(
                action=FeedbackAction.EXPAND,
                focus_points=[],
                questions=[],
                revision_instructions=feedback,
                confidence=0.5,
                raw_feedback=feedback
            )

    def generate_revision_prompt(
        self,
        analysis: FeedbackAnalysis,
        original_report: str,
        analyst_type: str,
        all_analyst_reports: dict = None
    ) -> str:
        """
        Generate a prompt for re-analysis based on feedback

        Args:
            analysis: Feedback analysis results
            original_report: The original analyst report
            analyst_type: Type of analyst
            all_analyst_reports: Dictionary of all previous analyst reports (for cross-reference)

        Returns:
            Prompt for re-analysis
        """
        parts = []

        parts.append("=== REVISION REQUEST ===\n")
        parts.append(f"The user has reviewed your {analyst_type} analysis and provided feedback.\n")

        if analysis.action == FeedbackAction.REVISE:
            parts.append("**Action Required**: REVISE your analysis based on user feedback.\n")
        elif analysis.action == FeedbackAction.EXPAND:
            parts.append("**Action Required**: EXPAND your analysis with more details.\n")
        elif analysis.action == FeedbackAction.CLARIFY:
            parts.append("**Action Required**: CLARIFY the following points.\n")
            parts.append("Note: User may be asking you to combine/explain data from other analysts.\n")

        if analysis.focus_points:
            parts.append(f"\n**Focus on these areas**:")
            for point in analysis.focus_points:
                parts.append(f"  - {point}")

        if analysis.questions:
            parts.append(f"\n**Answer these questions**:")
            for q in analysis.questions:
                parts.append(f"  - {q}")

        if analysis.revision_instructions:
            parts.append(f"\n**Specific Instructions**:\n{analysis.revision_instructions}")

        parts.append(f"\n**User's Original Feedback**: {analysis.raw_feedback}")

        # Include previous analysts' reports if user is asking for cross-analyst analysis
        if all_analyst_reports and (analysis.action == FeedbackAction.CLARIFY or "combine" in analysis.raw_feedback.lower() or "compare" in analysis.raw_feedback.lower()):
            parts.append("\n=== PREVIOUS ANALYSTS' REPORTS (for cross-reference) ===")
            parts.append("Use these reports to answer user's questions about combining/comparing data:\n")
            for prev_analyst_type, prev_report in all_analyst_reports.items():
                if prev_analyst_type != analyst_type:  # Don't include current analyst's own report
                    parts.append(f"\n--- {prev_analyst_type.upper()} ANALYST ---")
                    # Show first 1500 chars of each previous report
                    parts.append(prev_report[:1500] + "..." if len(prev_report) > 1500 else prev_report)

        parts.append("\n=== YOUR PREVIOUS ANALYSIS ===")
        parts.append(original_report[:1000] + "..." if len(original_report) > 1000 else original_report)

        parts.append("\n=== INSTRUCTIONS ===")
        if analysis.action == FeedbackAction.CLARIFY:
            parts.append("Answer the user's questions clearly and professionally.")
            parts.append("If user asks to combine data from multiple analysts, synthesize the information from the provided reports.")
            parts.append("Explain relationships and provide insights based on the combined data.")
        else:
            parts.append("Please revise your analysis addressing the above feedback.")
            parts.append("Keep what was good, improve what was questioned, and expand where requested.")
        parts.append("Maintain professional objectivity and analytical rigor.")

        return "\n".join(parts)


def create_feedback_analyzer(llm: BaseChatModel) -> FeedbackAnalyzer:
    """Factory function to create analyzer"""
    return FeedbackAnalyzer(llm)
