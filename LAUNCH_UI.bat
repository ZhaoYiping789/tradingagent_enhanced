@echo off
REM Interactive Trading Analysis UI Launcher
REM Double-click this file to start the UI

cd /d "%~dp0"

echo ========================================================================
echo    AI-Powered Trading Analysis Assistant
echo    Interactive UI Starting...
echo ========================================================================
echo.

REM Try to find Python
echo [INFO] Looking for Python...

REM Option 1: Try system Python
python --version >nul 2>&1
if not errorlevel 1 (
    echo [OK] System Python found
    set PYTHON_CMD=python
    goto :run_ui
)

REM Option 2: Try .venv Python
if exist ".venv\Scripts\python.exe" (
    echo [OK] Virtual environment Python found
    set PYTHON_CMD=.venv\Scripts\python.exe
    goto :run_ui
)

REM Option 3: Try uv
uv --version >nul 2>&1
if not errorlevel 1 (
    echo [OK] UV package manager found, using uv run
    set PYTHON_CMD=uv run python
    goto :run_ui
)

REM If nothing works
echo [ERROR] Could not find Python!
echo.
echo Please try one of these:
echo   1. Install Python 3.10+ and add to PATH
echo   2. Or run: uv sync
echo   3. Or manually run: .venv\Scripts\python.exe main_interactive_watsonx.py
echo.
pause
exit /b 1

:run_ui
echo [INFO] Starting UI on http://localhost:7860
echo.
echo When UI starts, open your browser to: http://localhost:7860
echo.
echo Press Ctrl+C to stop the server
echo ========================================================================
echo.

%PYTHON_CMD% main_interactive_watsonx.py

pause
