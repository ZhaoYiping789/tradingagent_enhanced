"""
Interactive WatsonX Trading Analysis System

Main entry point for the interactive Gradio UI with WatsonX integration.

Usage:
    python main_interactive_watsonx.py

    Then open your browser to http://localhost:7860
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

# WatsonX Configuration
WATSONX_CONFIG = {
    # LLM Provider
    "llm_provider": "watsonx",

    # WatsonX Connection Settings
    "watsonx_url": os.getenv("WATSONX_URL") or "https://us-south.ml.cloud.ibm.com",
    "watsonx_api_key": os.getenv("WATSONX_APIKEY") or os.getenv("WATSONX_API_KEY") or "1NlP-L5h1DDEZFKkvJ92uTuMFNbkk0pmGJ4lMutJ44w2",
    "watsonx_project_id": os.getenv("WATSONX_PROJECT_ID") or "394811a9-3e1c-4b80-8031-3fda71e6dce1",

    # Model Selection
    # Using Llama 3.3 70B (excellent quality, supported in your environment)
    # Alternative: ibm/granite-3-8b-instruct (faster, lighter)
    "deep_think_llm": "meta-llama/llama-3-3-70b-instruct",
    "quick_think_llm": "meta-llama/llama-3-3-70b-instruct",

    # Analysis Settings
    "max_debate_rounds": 2,
    "max_risk_discuss_rounds": 2,
    "enterprise_mode": True,
    "lightweight_quantitative": False,

    # Data Settings
    "online_tools": False,  # Set to False to use cached data for faster testing
    "backend_url": "http://localhost:8000",

    # Project directory (required)
    "project_dir": str(project_root),

    # Other Settings
    "verbose": True,
}


def validate_watsonx_config():
    """Validate WatsonX configuration"""
    required_keys = ["watsonx_api_key", "watsonx_project_id"]

    missing = []
    for key in required_keys:
        if not WATSONX_CONFIG.get(key):
            missing.append(key.upper())

    if missing:
        print("[ERROR] Missing required WatsonX configuration:")
        for key in missing:
            print(f"   - {key}")
        print("\nPlease set the following environment variables:")
        print("   - WATSONX_APIKEY")
        print("   - WATSONX_PROJECT_ID")
        print("\nOr edit WATSONX_CONFIG in this file directly.")
        return False

    return True


def main():
    """Launch the interactive UI"""

    print("=" * 70)
    print("AI-Powered Trading Analysis Assistant (WatsonX Edition)")
    print("=" * 70)
    print()

    # Validate configuration
    if not validate_watsonx_config():
        sys.exit(1)

    print("[OK] WatsonX configuration validated")
    print(f"[URL] {WATSONX_CONFIG['watsonx_url']}")
    print(f"[MODEL] {WATSONX_CONFIG['deep_think_llm']}")
    print()

    # Import and launch UI
    try:
        from tradingagents.interactive import launch_ui

        print("[LAUNCH] Starting Gradio UI...")
        print()
        print("[INFO] The UI will open in your browser at: http://localhost:7862")
        print("       (If it doesn't open automatically, visit that URL)")
        print()
        print("Press Ctrl+C to stop the server")
        print()
        print("-" * 70)

        # Launch with configuration
        launch_ui(
            config=WATSONX_CONFIG,
            server_name="0.0.0.0",
            server_port=7862,  # Using 7862 to avoid conflicts
            share=False,  # Set to True to create public link
            show_error=True
        )

    except KeyboardInterrupt:
        print("\n\n[SHUTDOWN] Shutting down gracefully...")

    except Exception as e:
        print(f"\n[ERROR] Error launching UI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
