@echo off
REM Simple UI Launcher - Double-click to run
REM This will show all output in the console window

cd /d "%~dp0"

echo ========================================================================
echo    AI Trading Analysis - Interactive UI
echo ========================================================================
echo.
echo Starting UI... Please wait...
echo.
echo Once started, open your browser to: http://localhost:7860
echo.
echo Press Ctrl+C to stop the server
echo ========================================================================
echo.

python test_ui_minimal.py

pause
