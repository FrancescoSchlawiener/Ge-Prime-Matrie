@echo off
chcp 65001 >nul 2>&1
setlocal EnableExtensions EnableDelayedExpansion
set "PYTHONIOENCODING=utf-8"
call "%~dp0_refresh_path.bat"
cd /d "%~dp0\.."
title GPM Workbench Setup
echo.
echo === GPM Workbench Setup ===
echo.

set "PY="
for /f "usebackq delims=" %%P in (`call "%~dp0_resolve_python.bat" 2^>nul`) do set "PY=%%P"

if not defined PY (
    echo [FEHLER] Kein Python 3.10+ mit venv-Modul gefunden.
    echo.
    echo Bitte start\doctor.bat ausfuehren fuer Details.
    echo.
    echo Moegliche Loesungen:
    echo   1. Python 3.10+ von https://www.python.org/downloads/ installieren
    echo      ^(Haken: "Add python.exe to PATH"^)
    echo   2. Nach Installation ein NEUES CMD-Fenster oeffnen ^(PATH wird sonst nicht aktualisiert^)
    echo   3. Windows Store-Alias deaktivieren:
    echo      Einstellungen ^> Apps ^> App-Ausfuehrungsaliase ^> python.exe AUS
    echo   4. Pfad manuell in GPM\workbench\.python-path eintragen
    echo.
    pause
    exit /b 1
)

echo [OK] Python: !PY!
echo !PY!>"%~dp0..\.python-path"

echo [INFO] Lege virtuelle Umgebung an ^(.venv^)...
for /f "usebackq delims=" %%P in (`"!PY!" "%~dp0find_python.py" --ensure-venv --print-path-only`) do set "PY=%%P"
if errorlevel 1 (
    echo.
    echo [FEHLER] ensure_venv fehlgeschlagen - siehe Meldungen oben.
    echo Tipp: start\doctor.bat ausfuehren
    pause
    exit /b 1
)

set "VENV_PYTHON=%~dp0..\.venv\Scripts\python.exe"
if not exist "!VENV_PYTHON!" (
    echo [FEHLER] .venv konnte nicht angelegt werden: !VENV_PYTHON!
    echo.
    echo Moegliche Loesungen:
    echo   1. Python 3.10+ von https://www.python.org/downloads/ installieren
    echo      ^(Haken: "Add python.exe to PATH"; venv-Modul muss verfuegbar sein^)
    echo   2. pgAdmin/PostgreSQL-Python ist NICHT geeignet - python.org verwenden
    echo   3. NEUES CMD-Fenster nach Installation oeffnen
    echo   4. start\doctor.bat ausfuehren
    echo.
    pause
    exit /b 1
)
if not defined PY set "PY=!VENV_PYTHON!"

echo [OK] Interpreter nach Discovery: !PY!
"!PY!" -m pip install --upgrade pip -q
if errorlevel 1 goto fail
"!PY!" -m pip install -r requirements.txt
if errorlevel 1 goto fail

"!PY!" "%~dp0bootstrap.py"
if errorlevel 1 goto fail

echo.
echo [OK] Setup fertig. Start mit: start\dev.bat
echo      ^(oder Doppelklick auf dev.bat im Ordner start\^)
echo.
pause
exit /b 0

:fail
echo [FEHLER] Setup fehlgeschlagen.
pause
exit /b 1
