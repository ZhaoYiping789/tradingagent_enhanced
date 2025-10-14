@echo off
REM Quick test script for WatsonX integration

echo ================================================================
echo WatsonX Integration Test
echo ================================================================
echo.

REM Set environment variables
echo Setting environment variables...
call set_watsonx_env.bat

echo.
echo ================================================================
echo Running connection test...
echo ================================================================
echo.

REM Run the test
python test_watsonx_connection.py

echo.
echo ================================================================
echo Test complete!
echo ================================================================
echo.
echo Next step: Run full analysis with:
echo   python main_enterprise_watsonx.py
echo.
pause
