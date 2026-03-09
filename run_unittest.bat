@echo off
set "PROJECT_DIR=%~dp0"
title Automated Backend Testing
echo ========================================
echo   Running Automated Backend Tests...
echo ========================================
echo.

:: Run the test using unittest
python -m unittest "%PROJECT_DIR%api\test_backend.py"

echo.
echo ========================================
echo   Tests Completed!
echo ========================================
pause
