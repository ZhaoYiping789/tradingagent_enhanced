"""
Diagnose UI launch issues
"""

import os
import sys
from pathlib import Path

# Fix encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, errors="replace")

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Step 1: Testing basic imports...")
try:
    import gradio as gr
    print("[OK] Gradio imported")
except Exception as e:
    print(f"[ERROR] Gradio import failed: {e}")
    sys.exit(1)

print("\nStep 2: Testing tradingagents import...")
try:
    from tradingagents.interactive import TradingAnalysisUI
    print("[OK] TradingAnalysisUI imported")
except Exception as e:
    print(f"[ERROR] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 3: Creating minimal config...")
config = {
    "llm_provider": "watsonx",
    "watsonx_url": "https://us-south.ml.cloud.ibm.com",
    "watsonx_api_key": "1NlP-L5h1DDEZFKkvJ92uTuMFNbkk0pmGJ4lMutJ44w2",
    "watsonx_project_id": "394811a9-3e1c-4b80-8031-3fda71e6dce1",
    "deep_think_llm": "meta-llama/llama-3-3-70b-instruct",
    "quick_think_llm": "meta-llama/llama-3-3-70b-instruct",
    "project_dir": str(project_root),
    "backend_url": "http://localhost:8000",
    "online_tools": False,
    "max_debate_rounds": 1,
    "enterprise_mode": False,
}
print("[OK] Config created")
print(f"[DEBUG] Config llm_provider: {config['llm_provider']}")

print("\nStep 4: Creating TradingAnalysisUI instance...")
try:
    ui = TradingAnalysisUI(config)
    print("[OK] UI instance created")
except Exception as e:
    print(f"[ERROR] UI creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 5: Creating Gradio app...")
try:
    app = ui.create_ui()
    print(f"[OK] Gradio app created")
except Exception as e:
    print(f"[ERROR] App creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 6: Launching on port 7862...")
print("[INFO] Opening http://localhost:7862 in your browser...")
print("[INFO] Press Ctrl+C to stop")
print("=" * 70)

try:
    app.launch(
        server_name="127.0.0.1",
        server_port=7862,
        share=False,
        show_error=True,
        quiet=False,
        inbrowser=True
    )
except Exception as e:
    print(f"\n[ERROR] Launch failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
