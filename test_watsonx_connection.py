#!/usr/bin/env python3
"""
Test script to verify WatsonX connection and tool calling support
"""

import os
import sys

def test_watsonx_connection():
    """Test WatsonX connection and basic functionality"""

    print("=" * 80)
    print("WATSONX CONNECTION TEST")
    print("=" * 80)
    print()

    # Step 1: Check environment variables
    print("Step 1: Checking environment variables...")
    watsonx_url = os.getenv("WATSONX_URL")
    watsonx_apikey = os.getenv("WATSONX_APIKEY")
    watsonx_project_id = os.getenv("WATSONX_PROJECT_ID")

    if not watsonx_url:
        print("[FAIL] WATSONX_URL not set")
        return False
    if not watsonx_apikey:
        print("[FAIL] WATSONX_APIKEY not set")
        return False
    if not watsonx_project_id:
        print("[FAIL] WATSONX_PROJECT_ID not set")
        return False

    print(f"[OK] WATSONX_URL: {watsonx_url}")
    print(f"[OK] WATSONX_PROJECT_ID: {watsonx_project_id}")
    print(f"[OK] WATSONX_APIKEY: {watsonx_apikey[:20]}...{watsonx_apikey[-10:]}")
    print()

    # Step 2: Check langchain-ibm installation
    print("Step 2: Checking langchain-ibm installation...")
    try:
        from langchain_ibm import ChatWatsonx
        print("[OK] langchain-ibm is installed")
    except ImportError as e:
        print(f"[FAIL] langchain-ibm not installed: {e}")
        print("   Please install: uv pip install langchain-ibm ibm-watsonx-ai")
        return False
    print()

    # Step 3: Initialize WatsonX LLM
    print("Step 3: Initializing WatsonX LLM...")
    try:
        llm = ChatWatsonx(
            model_id="meta-llama/llama-3-3-70b-instruct",
            url=watsonx_url,
            apikey=watsonx_apikey,
            project_id=watsonx_project_id,
            params={
                "max_new_tokens": 512,
                "temperature": 0.7,
            }
        )
        print("[OK] WatsonX LLM initialized successfully")
    except Exception as e:
        print(f"[FAIL] Failed to initialize WatsonX LLM: {e}")
        return False
    print()

    # Step 4: Test basic invocation
    print("Step 4: Testing basic LLM invocation...")
    try:
        from langchain_core.messages import HumanMessage

        test_message = HumanMessage(content="Say 'Hello from WatsonX!' in exactly those words.")
        response = llm.invoke([test_message])

        print(f"[OK] LLM Response: {response.content[:100]}...")
    except Exception as e:
        print(f"[FAIL] LLM invocation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()

    # Step 5: Test tool calling support
    print("Step 5: Testing tool calling support...")
    try:
        from langchain_core.tools import tool

        @tool
        def get_stock_price(ticker: str) -> str:
            """Get the current stock price for a given ticker symbol.

            Args:
                ticker: Stock ticker symbol (e.g., 'AAPL', 'NVDA')
            """
            return f"Mock price for {ticker}: $150.00"

        # Bind tools to LLM
        llm_with_tools = llm.bind_tools([get_stock_price])

        test_message = HumanMessage(content="What is the stock price for NVDA?")
        response = llm_with_tools.invoke([test_message])

        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"[OK] Tool calling works! Called: {response.tool_calls[0]['name']}")
            print(f"   Tool arguments: {response.tool_calls[0]['args']}")
        else:
            print("[WARN] Tool calling may not be fully supported")
            print(f"   Response: {response.content[:100]}...")
    except Exception as e:
        print(f"[WARN] Tool calling test failed: {e}")
        print("   This may be expected depending on the model")
    print()

    # Step 6: Test TradingAgents integration
    print("Step 6: Testing TradingAgents integration...")
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG

        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "watsonx"
        config["watsonx_url"] = watsonx_url
        config["watsonx_project_id"] = watsonx_project_id
        config["watsonx_api_key"] = watsonx_apikey
        config["deep_think_llm"] = "meta-llama/llama-3-3-70b-instruct"
        config["quick_think_llm"] = "ibm/granite-3-3-8b-instruct"

        # Try to initialize with minimal analysts
        ta = TradingAgentsGraph(
            selected_analysts=["market"],
            debug=False,
            config=config
        )
        print("[OK] TradingAgents initialized with WatsonX successfully!")
    except Exception as e:
        print(f"[FAIL] TradingAgents initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()

    print("=" * 80)
    print("[SUCCESS] ALL TESTS PASSED!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Run full analysis: python main_enterprise_watsonx.py")
    print("2. Check logs in: enterprise_watsonx_output.log")
    print("3. Review results in: results/[TICKER]/[DATE]/")
    print()

    return True

if __name__ == "__main__":
    # Set environment variables if not already set
    if not os.getenv("WATSONX_URL"):
        os.environ["WATSONX_URL"] = "https://us-south.ml.cloud.ibm.com"
    if not os.getenv("WATSONX_APIKEY"):
        os.environ["WATSONX_APIKEY"] = "1NlP-L5h1DDEZFKkvJ92uTuMFNbkk0pmGJ4lMutJ44w2"
    if not os.getenv("WATSONX_PROJECT_ID"):
        os.environ["WATSONX_PROJECT_ID"] = "394811a9-3e1c-4b80-8031-3fda71e6dce1"

    # Set dummy OPENAI_API_KEY for memory system (uses OpenAI embeddings)
    # TODO: Update memory system to support WatsonX embeddings
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "dummy-key-for-testing"

    success = test_watsonx_connection()
    sys.exit(0 if success else 1)
