@echo off
goto :main

:_scan_pythoncore
set "_ROOT=%~1"
if not exist "!_ROOT!" exit /b 1
for /f "delims=" %%D in ('dir /b /ad /o-n "!_ROOT!\pythoncore-*" 2^>nul') do call :_try_path "!_ROOT!\%%D\python.exe" & if !errorlevel! equ 0 exit /b 0
if exist "!_ROOT!\bin\python.exe" call :_try_path "!_ROOT!\bin\python.exe" & if !errorlevel! equ 0 exit /b 0
exit /b 1

:_scan_python_root
set "_ROOT=%~1"
if not exist "!_ROOT!" exit /b 1
for /f "delims=" %%D in ('dir /b /ad /o-n "!_ROOT!\Python3*" 2^>nul') do call :_try_path "!_ROOT!\%%D\python.exe" & if !errorlevel! equ 0 exit /b 0
exit /b 1

:_try_path
call :_emit_if_valid "%~1"
exit /b %errorlevel%

:_emit_if_valid
set "_CAND=%~1"
if not defined _CAND exit /b 1
set "_CHK=!_CAND:WindowsApps=!"
if not "!_CHK!"=="!_CAND!" exit /b 1
set "_CHK=!_CAND:windowsapps=!"
if not "!_CHK!"=="!_CAND!" exit /b 1
if not exist "!_CAND!" exit /b 1
call :_validate "!_CAND!"
if !errorlevel! neq 0 exit /b 1
echo !_CAND!
exit /b 0

:_validate
set "_EXE=%~1"
if not exist "!_EXE!" exit /b 1
"!_EXE!" "%~dp0_py_ok.py" >nul 2>nul
if !errorlevel! neq 0 exit /b 1
"!_EXE!" -m venv --help >nul 2>nul
exit /b !errorlevel!

:main
rem Discover Python 3.10+ with venv. Call via: call "%~dp0_resolve_python.bat"
setlocal EnableExtensions EnableDelayedExpansion
call "%~dp0_refresh_path.bat"
set "START_DIR=%~dp0"
set "ROOT=%START_DIR%.."
set "PY_PATH_FILE=%ROOT%\.python-path"

if exist "%PY_PATH_FILE%" set /p _CAND=<"%PY_PATH_FILE%"
if exist "%PY_PATH_FILE%" if exist "!_CAND!" call :_emit_if_valid "!_CAND!"
if exist "%PY_PATH_FILE%" if exist "!_CAND!" if !errorlevel! equ 0 exit /b 0

call :_scan_pythoncore "%LOCALAPPDATA%\Python"
if !errorlevel! equ 0 exit /b 0

where py >nul 2>nul
if !errorlevel! neq 0 goto :after_py_launcher
py -3 "%START_DIR%_py_ok.py" >nul 2>nul
if !errorlevel! neq 0 goto :after_py_launcher
for /f "delims=" %%P in ('py -3 "%START_DIR%_which_py.py" 2^>nul') do call :_emit_if_valid "%%P" & if !errorlevel! equ 0 exit /b 0
:after_py_launcher

call :_scan_python_root "%LOCALAPPDATA%\Programs\Python"
if !errorlevel! equ 0 exit /b 0
call :_scan_python_root "%APPDATA%\Python"
if !errorlevel! equ 0 exit /b 0
call :_scan_python_root "%ProgramFiles%"
if !errorlevel! equ 0 exit /b 0
call :_scan_python_root "C:\"
if !errorlevel! equ 0 exit /b 0

for /f "delims=" %%P in ('where python 2^>nul') do call :_try_path "%%P" & if !errorlevel! equ 0 exit /b 0
for /f "delims=" %%P in ('where python3 2^>nul') do call :_try_path "%%P" & if !errorlevel! equ 0 exit /b 0

set "_PROBE="
where py >nul 2>nul
if !errorlevel! equ 0 set "_PROBE=py -3"
if defined _PROBE goto :probe_done
where python >nul 2>nul
if !errorlevel! equ 0 set "_PROBE=python"
:probe_done
if defined _PROBE for /f "delims=" %%P in (`!_PROBE! "%START_DIR%find_python.py" --print-path-only 2^>nul`) do call :_try_path "%%P" & if !errorlevel! equ 0 exit /b 0

call :_try_path "%ProgramFiles%\pgAdmin 4\python\python.exe"
if !errorlevel! equ 0 exit /b 0
call :_try_path "%ProgramFiles%\PostgreSQL\18\pgAdmin 4\python\python.exe"
if !errorlevel! equ 0 exit /b 0
call :_try_path "%ProgramFiles%\PostgreSQL\17\pgAdmin 4\python\python.exe"
if !errorlevel! equ 0 exit /b 0

exit /b 1
