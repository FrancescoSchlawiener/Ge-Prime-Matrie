@echo off
REM Einmal-Setup: .venv anlegen, Abhaengigkeiten, Python-Pfad fuer IDE merken
chcp 65001 >nul 2>&1
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
set "ROOT=%CD%"

echo.
echo === Ge-Prime-Matrix Setup (.venv) ===
echo.

call :find_python
if not defined PY goto die

echo Basis-Python: !PY!
echo Erstelle/aktualisiere .venv ...
"!PY!" scripts\find_python.py --ensure-venv
if errorlevel 1 goto die

for /f "delims=" %%P in ('"!PY!" scripts\find_python.py --print') do set "PY=%%P"
if exist ".venv\Scripts\python.exe" set "PY=%ROOT%\.venv\Scripts\python.exe"
echo Projekt-Python: !PY!

"!PY!" -m pip install --upgrade pip -q
"!PY!" -m pip install -r requirements.txt
if errorlevel 1 goto die

"!PY!" scripts\bootstrap.py
if errorlevel 1 goto die

echo.
echo [OK] Setup fertig.
echo     Python fuer dieses Projekt: .venv\Scripts\python.exe
echo     Cursor/VS Code nutzt .vscode\settings.json automatisch.
echo     Terminal: dev.bat run_tests.py
echo     Stoppen:  stop.bat
echo.
goto die

:find_python
if exist ".venv\Scripts\python.exe" (
    set "PY=%ROOT%\.venv\Scripts\python.exe"
    goto :eof
)
for %%P in (
    "%ProgramFiles%\pgAdmin 4\python\python.exe"
    "%ProgramFiles%\PostgreSQL\18\pgAdmin 4\python\python.exe"
    "%ProgramFiles%\PostgreSQL\17\pgAdmin 4\python\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) do (
    if exist %%P (
        "%%~P" -c "import sys" >nul 2>&1
        if not errorlevel 1 (
            set "PY=%%~P"
            goto :eof
        )
    )
)
where py >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%P"
)
if defined PY goto :eof
echo [FEHLER] Kein Python 3 gefunden.
exit /b 1

:die
pause
