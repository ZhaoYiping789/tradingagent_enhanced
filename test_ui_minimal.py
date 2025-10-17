"""
Minimal UI test to diagnose issues
"""

import os
import sys
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, errors="replace")

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Testing Interactive UI Components")
print("=" * 70)

# Step 1: Test imports
print("\n[1/5] Testing imports...")
try:
    from tradingagents.interactive import TradingAnalysisUI
    print("✅ TradingAnalysisUI imported")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Create config
print("\n[2/5] Creating configuration...")
config = {
    "llm_provider": "watsonx",
    "watsonx_url": "https://us-south.ml.cloud.ibm.com",
    "watsonx_api_key": "1NlP-L5h1DDEZFKkvJ92uTuMFNbkk0pmGJ4lMutJ44w2",
    "watsonx_project_id": "394811a9-3e1c-4b80-8031-3fda71e6dce1",
    "deep_think_llm": "mistralai/mixtral-8x7b-instruct-v01",
    "quick_think_llm": "mistralai/mixtral-8x7b-instruct-v01",
    "max_debate_rounds": 2,
    "enterprise_mode": True,
    "online_tools": False,  # Use offline for testing
    "project_dir": str(project_root),
    "backend_url": "http://localhost:8000",
}
print("✅ Configuration created")

# Step 3: Create UI instance
print("\n[3/5] Creating UI instance...")
try:
    ui = TradingAnalysisUI(config)
    print("✅ UI instance created")
except Exception as e:
    print(f"❌ UI instance creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Create Gradio app
print("\n[4/5] Creating Gradio app...")
try:
    app = ui.create_ui()
    print(f"✅ Gradio app created (type: {type(app).__name__})")
except Exception as e:
    print(f"❌ Gradio app creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Try to launch
print("\n[5/5] Launching Gradio UI...")
print("📱 The UI should open at: http://localhost:7861")
print("   (Using port 7861 to avoid conflicts)")
print("\nPress Ctrl+C to stop")
print("=" * 70)

try:
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,  # Different port
        share=False,
        show_error=True,
        quiet=False
    )
except KeyboardInterrupt:
    print("\n\n👋 Shutting down...")
except Exception as e:
    print(f"\n❌ Launch failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
