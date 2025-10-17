@echo off
REM Interactive Trading Analysis UI Launcher (WatsonX)
REM
REM This script launches the Gradio web interface for interactive stock analysis.

echo ========================================================================
echo    AI-Powered Trading Analysis Assistant (WatsonX Edition)
echo    Interactive Gradio UI Launcher
echo ========================================================================
echo.

REM Set WatsonX credentials (edit these values or set as environment variables)
set WATSONX_URL=https://us-south.ml.cloud.ibm.com
set WATSONX_APIKEY=1NlP-L5h1DDEZFKkvJ92uTuMFNbkk0pmGJ4lMutJ44w2
set WATSONX_PROJECT_ID=394811a9-3e1c-4b80-8031-3fda71e6dce1

echo WatsonX Configuration:
echo   URL: %WATSONX_URL%
echo   Project ID: %WATSONX_PROJECT_ID%
echo.

echo Launching Interactive UI...
echo The UI will open at: http://localhost:7860
echo.
echo Press Ctrl+C to stop the server
echo ========================================================================
echo.

REM Launch the UI
uv run python main_interactive_watsonx.py

pause
