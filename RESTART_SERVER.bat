@echo off
echo Killing all Flask processes...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting Flask server with portfolio fixes...
cd /d "C:\Users\User\Desktop\TradingAgents-main"
start "" cmd /k "uv run python flask_chat_app.py"

echo.
echo Server restarting... Please check the new window.
echo URL: http://localhost:7862
pause
