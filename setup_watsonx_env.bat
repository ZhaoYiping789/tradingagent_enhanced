@echo off
REM Setup script for WatsonX environment using UV package manager (Windows)

echo ==================================================
echo TradingAgents WatsonX Environment Setup
echo ==================================================
echo.

REM Create and sync WatsonX environment with UV
echo Creating WatsonX environment with UV...
uv venv watsonx_env

echo.
echo Activating environment...
call watsonx_env\Scripts\activate.bat

echo.
echo Installing dependencies from pyproject-watsonx.toml...
uv pip install -e . --config-settings pyproject=pyproject-watsonx.toml

echo.
echo Verifying langchain-ibm installation...
uv pip show langchain-ibm

echo.
echo ==================================================
echo WatsonX Environment Setup Complete!
echo ==================================================
echo.
echo To activate this environment:
echo   watsonx_env\Scripts\activate.bat
echo.
echo Required environment variables:
echo   set WATSONX_API_KEY=your-api-key
echo   set WATSONX_PROJECT_ID=your-project-id
echo   set WATSONX_URL=https://us-south.ml.cloud.ibm.com
echo.
pause
