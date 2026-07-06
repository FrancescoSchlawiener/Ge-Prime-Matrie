@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
set "PYTHONIOENCODING=utf-8"
call "%~dp0_refresh_path.bat"
title GPM Workbench Server Launchpad
cd /d "%~dp0\.."

echo ====================================================================
echo [GPM WORKBENCH] Initialisiere kaskadierende Laufzeit-Kalibrierung...
echo ====================================================================

set "PY="
for /f "usebackq delims=" %%P in (`call "%~dp0_resolve_python.bat" 2^>nul`) do set "PY=%%P"

if not defined PY (
    echo [FATAL ERROR] Es konnte kein valider Python 3.10+ Interpreter gefunden werden.
    echo [INFO] Invariante P1-B: 0-Byte-Stubs ^(WindowsApps^) wurden rigoros verworfen.
    echo.
    echo Bitte start\doctor.bat ausfuehren, dann start\setup.bat.
    echo Nach Python-Installation: NEUES CMD-Fenster oeffnen!
    echo Siehe: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] System-Interpreter: !PY!

set "PY_PATH_FILE=%~dp0..\.python-path"
echo !PY!>"!PY_PATH_FILE!"

for /f "usebackq delims=" %%P in (`"!PY!" "%~dp0find_python.py" --print-path-only 2^>nul`) do set "PY=%%P"
if defined PY echo [OK] Discovery verfeinert: !PY!

:venv_check
set "VENV_PYTHON=%~dp0..\.venv\Scripts\python.exe"
if not exist "!VENV_PYTHON!" (
    echo [INFO] Virtuelle Umgebung fehlt. Starte System-Bootstrapping...
    "!PY!" "%~dp0bootstrap.py"
    if !errorlevel! neq 0 (
        echo [FATAL ERROR] Bootstrapping fehlgeschlagen. Bitte start\setup.bat ausfuehren.
        echo Tipp: start\doctor.bat
        pause
        exit /b 1
    )
)

if not exist "!VENV_PYTHON!" (
    echo [FATAL ERROR] .venv fehlt nach Bootstrap: !VENV_PYTHON!
    echo [INFO] Installieren Sie Python 3.10+ von https://www.python.org/downloads/
    echo        ^(Haken: "Add python.exe to PATH"; venv-Modul muss verfuegbar sein^)
    echo [INFO] pgAdmin/PostgreSQL-Python ist nicht geeignet - bitte python.org verwenden.
    echo [INFO] Nach Installation: NEUES CMD-Fenster, dann start\setup.bat
    echo [INFO] Diagnose: start\doctor.bat
    pause
    exit /b 1
)

echo [SUCCESS] Laufzeit-Kalibrierung abgeschlossen. Zuende API + Vite-Proxy...
"!VENV_PYTHON!" "%~dp0run_dev.py" %*
exit /b %ERRORLEVEL%
