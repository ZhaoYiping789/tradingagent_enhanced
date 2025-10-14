#!/bin/bash
# Setup script for WatsonX environment using UV package manager

echo "=================================================="
echo "TradingAgents WatsonX Environment Setup"
echo "=================================================="
echo ""

# Create and sync WatsonX environment with UV
echo "Creating WatsonX environment with UV..."
uv venv watsonx_env

echo ""
echo "Activating environment..."
source watsonx_env/bin/activate || source watsonx_env/Scripts/activate

echo ""
echo "Installing dependencies from pyproject-watsonx.toml..."
uv pip install -e . --config-settings pyproject=pyproject-watsonx.toml

echo ""
echo "Verifying langchain-ibm installation..."
uv pip show langchain-ibm

echo ""
echo "=================================================="
echo "WatsonX Environment Setup Complete!"
echo "=================================================="
echo ""
echo "To activate this environment:"
echo "  source watsonx_env/bin/activate"
echo "  (or on Windows: watsonx_env\\Scripts\\activate)"
echo ""
echo "Required environment variables:"
echo "  export WATSONX_API_KEY='your-api-key'"
echo "  export WATSONX_PROJECT_ID='your-project-id'"
echo "  export WATSONX_URL='https://us-south.ml.cloud.ibm.com'"
echo ""
