@echo off
title Running Dashboard Monitor
echo Starting Backend Server...
start /min "" python "d:\YUP\monitor\api\backend_server.py"
timeout /t 3 >nul
echo Opening Dashboard...
start "" "d:\YUP\monitor\login\login.html"
exit
