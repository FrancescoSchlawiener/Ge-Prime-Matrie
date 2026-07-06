@echo off
rem Prepend registry PATH + Python install dirs; never discard existing PATH (keeps System32).
setlocal EnableExtensions EnableDelayedExpansion
set "_PATH=%PATH%"

set "_MERGED="
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "_MERGED=%%b"
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do (
    if defined _MERGED (set "_MERGED=!_MERGED!;%%b") else (set "_MERGED=%%b")
)
if defined _MERGED set "_PATH=!_MERGED!;!_PATH!"

if not defined LOCALAPPDATA set "LOCALAPPDATA=%USERPROFILE%\AppData\Local"
if not defined APPDATA set "APPDATA=%USERPROFILE%\AppData\Roaming"

if exist "!LOCALAPPDATA!\Programs\Python" (
    for /d %%D in ("!LOCALAPPDATA!\Programs\Python\Python3*") do (
        set "_PATH=%%~fD;%%~fD\Scripts;!_PATH!"
    )
)
if exist "!LOCALAPPDATA!\Python" (
    for /d %%D in ("!LOCALAPPDATA!\Python\pythoncore-*") do (
        set "_PATH=%%~fD;%%~fD\Scripts;!_PATH!"
    )
    if exist "!LOCALAPPDATA!\Python\bin" (
        set "_PATH=!LOCALAPPDATA!\Python\bin;!_PATH!"
    )
)
if exist "!APPDATA!\Python" (
    for /d %%D in ("!APPDATA!\Python\Python3*") do (
        set "_PATH=%%~fD;%%~fD\Scripts;!_PATH!"
    )
)
if exist "!ProgramFiles!" (
    for /d %%D in ("!ProgramFiles!\Python3*") do (
        set "_PATH=%%~fD;%%~fD\Scripts;!_PATH!"
    )
)

set "GPM_PATH_TMP=%TEMP%\gpm_workbench_path_%USERNAME%.tmp"
> "!GPM_PATH_TMP!" echo(!_PATH!)
endlocal
set /p PATH=<"%TEMP%\gpm_workbench_path_%USERNAME%.tmp"
del "%TEMP%\gpm_workbench_path_%USERNAME%.tmp" 2>nul
exit /b 0
