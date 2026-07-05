@echo off
REM Ge-Prime-Server auf Port 5000 sauber beenden (nur run_server.py)
chcp 65001 >nul 2>&1
setlocal EnableExtensions
cd /d "%~dp0"
if not defined PORT set "PORT=5000"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" scripts\server_control.py --port %PORT%
) else (
    call dev.bat scripts\server_control.py --port %PORT%
)
set "EXITCODE=%ERRORLEVEL%"
echo.
pause
exit /b %EXITCODE%
