@echo off
REM Projekt-Python: .venv > .python-path > pgAdmin/system
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" %*
    exit /b %ERRORLEVEL%
)

if exist ".python-path" (
    set /p PY=<".python-path"
    if exist "!PY!" (
        "!PY!" %*
        exit /b %ERRORLEVEL%
    )
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
            "%%~P" %*
            exit /b %ERRORLEVEL%
        )
    )
)

where py >nul 2>&1
if not errorlevel 1 (
    py -3 %*
    exit /b %ERRORLEVEL%
)

echo [FEHLER] Kein Python — einmal setup.bat ausfuehren.
exit /b 1
