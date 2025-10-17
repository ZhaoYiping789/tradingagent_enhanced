"""
User Preference Parser Module

Analyzes natural language user input to extract structured preferences,
constraints, and focus areas for trading analysis.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel


@dataclass
class UserPreferences:
    """Structured user preferences for analysis"""

    # Key metrics/indicators user wants to focus on
    focus_areas: List[str]

    # Analysis principles and methodologies user prefers
    principles: List[str]

    # Things to avoid or constraints
    constraints: List[str]

    # Risk tolerance (conservative, moderate, aggressive)
    risk_tolerance: str

    # Investment horizon (short-term, medium-term, long-term)
    investment_horizon: str

    # Additional custom instructions
    custom_instructions: str

    # Original raw input
    raw_input: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_prompt_context(self) -> str:
        """Convert to formatted text for prompt injection"""
        parts = []

        parts.append("=== USER PREFERENCES AND REQUIREMENTS ===\n")

        if self.focus_areas:
            parts.append(f"📊 FOCUS AREAS: {', '.join(self.focus_areas)}")

        if self.principles:
            parts.append(f"📋 ANALYSIS PRINCIPLES: {', '.join(self.principles)}")

        if self.constraints:
            parts.append(f"⚠️ CONSTRAINTS/AVOID: {', '.join(self.constraints)}")

        parts.append(f"🎯 RISK TOLERANCE: {self.risk_tolerance}")
        parts.append(f"⏰ INVESTMENT HORIZON: {self.investment_horizon}")

        if self.custom_instructions:
            parts.append(f"💡 CUSTOM INSTRUCTIONS: {self.custom_instructions}")

        parts.append("\n=== END USER PREFERENCES ===\n")
        parts.append("IMPORTANT: Incorporate these preferences into your analysis while maintaining professional objectivity.")

        return "\n".join(parts)


class UserPreferenceParser:
    """Parses natural language user input into structured preferences"""

    SYSTEM_PROMPT = """You are an expert financial analyst assistant that extracts structured information from user preferences.

Your task is to analyze the user's natural language input and extract:
1. Focus areas - specific metrics, indicators, or aspects they want to emphasize
2. Principles - analytical methodologies or approaches they prefer
3. Constraints - things to avoid or restrictions
4. Risk tolerance - conservative, moderate, or aggressive
5. Investment horizon - short-term, medium-term, or long-term
6. Custom instructions - any other specific requirements

Return a JSON object with these fields:
{
  "focus_areas": ["list", "of", "focus", "areas"],
  "principles": ["list", "of", "principles"],
  "constraints": ["list", "of", "constraints"],
  "risk_tolerance": "conservative|moderate|aggressive",
  "investment_horizon": "short-term|medium-term|long-term",
  "custom_instructions": "any additional instructions"
}

If the user doesn't specify something, use reasonable defaults:
- risk_tolerance: "moderate"
- investment_horizon: "medium-term"
- Empty lists for areas not mentioned

Be intelligent in extracting meaning. For example:
- "I care about profitability" -> focus_areas: ["profitability", "earnings", "profit margins"]
- "Don't trust technical indicators alone" -> constraints: ["over-reliance on technical indicators"]
- "I'm risk-averse" -> risk_tolerance: "conservative"
"""

    def __init__(self, llm: BaseChatModel):
        """
        Initialize parser

        Args:
            llm: Language model for parsing
        """
        self.llm = llm

    def parse(self, user_input: str) -> UserPreferences:
        """
        Parse user input into structured preferences

        Args:
            user_input: Natural language user preferences

        Returns:
            UserPreferences object
        """
        if not user_input or not user_input.strip():
            # Return defaults if no input
            return UserPreferences(
                focus_areas=[],
                principles=[],
                constraints=[],
                risk_tolerance="moderate",
                investment_horizon="medium-term",
                custom_instructions="",
                raw_input=""
            )

        # Call LLM to parse preferences
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"User input:\n{user_input}\n\nExtract preferences as JSON:")
        ]

        response = self.llm.invoke(messages)

        # Parse JSON response
        try:
            # Extract JSON from response
            content = response.content

            # Try to find JSON in response
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            parsed_data = json.loads(json_str)

            # Create UserPreferences object
            preferences = UserPreferences(
                focus_areas=parsed_data.get("focus_areas", []),
                principles=parsed_data.get("principles", []),
                constraints=parsed_data.get("constraints", []),
                risk_tolerance=parsed_data.get("risk_tolerance", "moderate"),
                investment_horizon=parsed_data.get("investment_horizon", "medium-term"),
                custom_instructions=parsed_data.get("custom_instructions", ""),
                raw_input=user_input
            )

            return preferences

        except (json.JSONDecodeError, IndexError, KeyError) as e:
            print(f"Warning: Failed to parse LLM response: {e}")
            print(f"Response content: {response.content}")

            # Return defaults with raw input
            return UserPreferences(
                focus_areas=[],
                principles=[],
                constraints=[],
                risk_tolerance="moderate",
                investment_horizon="medium-term",
                custom_instructions=user_input,  # Store as custom instructions
                raw_input=user_input
            )

    def generate_analyst_instructions(
        self,
        preferences: UserPreferences,
        analyst_type: str
    ) -> str:
        """
        Generate specific instructions for an analyst based on user preferences

        Args:
            preferences: User preferences
            analyst_type: Type of analyst (e.g., 'market', 'fundamentals', 'news')

        Returns:
            Formatted instruction string to inject into analyst prompt
        """
        # Base context
        context = preferences.to_prompt_context()

        # Add analyst-specific guidance
        analyst_guidance = {
            "market": "Pay special attention to technical indicators and price patterns mentioned in user preferences.",
            "fundamentals": "Focus on financial metrics and ratios specified by the user.",
            "news": "Prioritize news themes and sentiment aspects highlighted by the user.",
            "social": "Analyze social sentiment through the lens of user's risk tolerance.",
            "comprehensive_quantitative": "Weight forecasting models according to user's investment horizon.",
            "portfolio": "Consider portfolio implications based on user's risk tolerance.",
            "enterprise_strategy": "Align strategic recommendations with user's principles and constraints."
        }

        guidance = analyst_guidance.get(analyst_type, "Apply user preferences to your analysis.")

        return f"{context}\n\n**Analyst-Specific Guidance**: {guidance}"


def create_preference_parser(llm: BaseChatModel) -> UserPreferenceParser:
    """Factory function to create parser"""
    return UserPreferenceParser(llm)
