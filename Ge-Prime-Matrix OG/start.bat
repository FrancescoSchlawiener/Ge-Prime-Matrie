@echo off
chcp 65001 >nul 2>&1
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"
set "ROOT=%CD%"
set "VENV=%ROOT%\.venv"
set "PY="
set "EXITCODE=1"

title Ge-Prime-Matrix

echo.
echo === Ge-Prime-Matrix Start ===
echo.

REM Alte lokale Instanz beenden (nur Ge-Prime, nicht andere Dienste)
if exist "%VENV%\Scripts\python.exe" (
    "%VENV%\Scripts\python.exe" scripts\server_control.py --port 5000 >nul 2>&1
) else (
    call :find_python
    if defined PY "!PY!" scripts\server_control.py --port 5000 >nul 2>&1
)

if exist "%VENV%\Scripts\python.exe" (
    set "PY=%VENV%\Scripts\python.exe"
    goto :have_py
)

if exist "%ROOT%\.python-path" (
    set /p PY=<"%ROOT%\.python-path"
    if exist "!PY!" goto :have_py
)

call :find_python
if not defined PY goto die

echo Registriere Projekt-Python ^(.python-path^)...
"!PY!" scripts\find_python.py --ensure-venv
if errorlevel 1 goto die

if exist "%VENV%\Scripts\python.exe" (
    set "PY=%VENV%\Scripts\python.exe"
) else if exist "%ROOT%\.python-path" (
    set /p PY=<"%ROOT%\.python-path"
)

:have_py
echo Python: !PY!

echo Aktualisiere pip...
"!PY!" -m pip install --upgrade pip -q

echo Installiere Abhaengigkeiten...
"!PY!" -m pip install -r requirements.txt
if errorlevel 1 goto die

echo Initialisiere Datenbank...
"!PY!" scripts\bootstrap.py
if errorlevel 1 goto die

"!PY!" scripts\run_server.py --verify-ui
if errorlevel 1 goto die

echo Start aus: %ROOT%
echo URL: http://127.0.0.1:5000
echo Stoppen: stop.bat oder Strg+C
echo.

set "FLASK_DEBUG=0"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
set "PORT=5000"
set "HOST=127.0.0.1"
set "OPEN_BROWSER=1"
"!PY!" scripts\run_server.py
set "EXITCODE=%ERRORLEVEL%"

echo.
if not "!EXITCODE!"=="0" (
    echo [FEHLER] Server beendet mit Code !EXITCODE!.
) else (
    echo Server beendet.
)
goto die

:find_python
if exist "%VENV%\Scripts\python.exe" (
    set "PY=%VENV%\Scripts\python.exe"
    goto :eof
)
for %%P in (
    "%ProgramFiles%\pgAdmin 4\python\python.exe"
    "%ProgramFiles%\PostgreSQL\18\pgAdmin 4\python\python.exe"
    "%ProgramFiles%\PostgreSQL\17\pgAdmin 4\python\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
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
echo [FEHLER] Kein Python 3 gefunden — bitte setup.bat ausfuehren.
exit /b 1

:die
echo.
pause
exit /b %EXITCODE%
