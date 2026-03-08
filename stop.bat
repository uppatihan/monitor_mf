@echo off
title Stopping Dashboard Monitor
echo Stopping Backend Server (Flask)...
taskkill /F /FI "WINDOWTITLE eq Running Dashboard Monitor*" /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1
echo DONE!
timeout /t 2
exit
