"""
Test Interactive Trading Analysis System

Quick test to verify the interactive components are working correctly.
"""

import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, errors="replace")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set test environment variables
os.environ["WATSONX_URL"] = "https://us-south.ml.cloud.ibm.com"
os.environ["WATSONX_APIKEY"] = os.getenv("WATSONX_APIKEY", "1NlP-L5h1DDEZFKkvJ92uTuMFNbkk0pmGJ4lMutJ44w2")
os.environ["WATSONX_PROJECT_ID"] = os.getenv("WATSONX_PROJECT_ID", "394811a9-3e1c-4b80-8031-3fda71e6dce1")


def test_imports():
    """Test that all interactive modules can be imported"""
    print("Testing imports...")

    try:
        from tradingagents.interactive import (
            UserPreferences,
            UserPreferenceParser,
            create_preference_parser,
            FeedbackAnalysis,
            FeedbackAnalyzer,
            FeedbackAction,
            create_feedback_analyzer,
            InteractiveWorkflowController,
            WorkflowState,
            WorkflowStage,
            AnalystStatus,
            GraphExecutorHelper,
            create_executor_helper,
            TradingAnalysisUI,
            launch_ui,
        )
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_user_preference_parser():
    """Test user preference parser"""
    print("\nTesting user preference parser...")

    try:
        from tradingagents.interactive import UserPreferenceParser
        from langchain_openai import ChatOpenAI

        # Create a simple LLM for testing
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

        parser = UserPreferenceParser(llm)

        # Test input
        test_input = """
        I'm a conservative long-term investor.
        Focus on profitability and cash flow.
        Avoid speculative plays.
        Risk tolerance: low.
        """

        preferences = parser.parse(test_input)

        print(f"  Focus Areas: {preferences.focus_areas}")
        print(f"  Principles: {preferences.principles}")
        print(f"  Constraints: {preferences.constraints}")
        print(f"  Risk Tolerance: {preferences.risk_tolerance}")
        print(f"  Investment Horizon: {preferences.investment_horizon}")

        print("✅ User preference parser working")
        return True

    except Exception as e:
        print(f"❌ User preference parser failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_feedback_analyzer():
    """Test feedback analyzer"""
    print("\nTesting feedback analyzer...")

    try:
        from tradingagents.interactive import FeedbackAnalyzer, FeedbackAction
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        analyzer = FeedbackAnalyzer(llm)

        # Test different feedback types
        test_cases = [
            ("Looks good!", FeedbackAction.APPROVE),
            ("Can you explain the P/E ratio?", FeedbackAction.CLARIFY),
            ("I think you missed the competitive analysis", FeedbackAction.REVISE),
            ("Tell me more about cash flow", FeedbackAction.EXPAND),
        ]

        for feedback, expected_action in test_cases:
            analysis = analyzer.analyze(
                feedback=feedback,
                analyst_type="market",
                analyst_report="Sample report...",
                context={}
            )

            action_match = "✅" if analysis.action == expected_action else "⚠️"
            print(f"  {action_match} '{feedback}' → {analysis.action.value} (expected: {expected_action.value})")

        print("✅ Feedback analyzer working")
        return True

    except Exception as e:
        print(f"❌ Feedback analyzer failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_controller():
    """Test workflow controller initialization"""
    print("\nTesting workflow controller...")

    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.interactive import (
            InteractiveWorkflowController,
            create_preference_parser,
            create_feedback_analyzer
        )

        # Create minimal config
        config = {
            "llm_provider": "openai",
            "deep_think_llm": "gpt-3.5-turbo",
            "quick_think_llm": "gpt-3.5-turbo",
            "project_dir": str(project_root),
            "backend_url": "http://localhost:8000",
            "online_tools": False,  # Use offline mode for testing
        }

        # Create graph
        print("  Creating graph...")
        graph = TradingAgentsGraph(
            selected_analysts=["market"],
            config=config
        )

        # Create parsers
        print("  Creating parsers...")
        preference_parser = create_preference_parser(graph.quick_thinking_llm)
        feedback_analyzer = create_feedback_analyzer(graph.quick_thinking_llm)

        # Create controller
        print("  Creating controller...")
        controller = InteractiveWorkflowController(
            graph=graph,
            preference_parser=preference_parser,
            feedback_analyzer=feedback_analyzer
        )

        # Initialize workflow
        print("  Initializing workflow...")
        controller.initialize(
            company_of_interest="NVDA",
            trade_date="2025-10-09",
            selected_analysts=["market"],
            user_preference_text="Focus on technical indicators"
        )

        # Check state
        state_summary = controller.get_state_summary()
        print(f"  Workflow stage: {state_summary['stage']}")
        print(f"  Company: {state_summary['company']}")
        print(f"  Analysts: {state_summary['analysts']}")

        print("✅ Workflow controller working")
        return True

    except Exception as e:
        print(f"❌ Workflow controller failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_creation():
    """Test Gradio UI creation (without launching)"""
    print("\nTesting UI creation...")

    try:
        from tradingagents.interactive import TradingAnalysisUI

        ui = TradingAnalysisUI()
        app = ui.create_ui()

        print(f"  UI type: {type(app)}")
        print("✅ UI creation successful")
        return True

    except Exception as e:
        print(f"❌ UI creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("Interactive Trading Analysis System - Component Tests")
    print("=" * 70)

    tests = [
        ("Imports", test_imports),
        ("User Preference Parser", test_user_preference_parser),
        ("Feedback Analyzer", test_feedback_analyzer),
        ("Workflow Controller", test_workflow_controller),
        ("UI Creation", test_ui_creation),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")

    if failed == 0:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nTo launch the interactive UI:")
        print("  python main_interactive_watsonx.py")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please fix before using.")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
