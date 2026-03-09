@echo off
set "PROJECT_DIR=%~dp0"
title Running Dashboard Monitor
echo Starting ...
start /min "" python "%PROJECT_DIR%api\backend_server.py"
timeout /t 3 >nul
echo Opening Dashboard...
start "" "%PROJECT_DIR%login\login.html"
exit
