@echo off
chcp 65001 >nul 2>&1
setlocal EnableExtensions EnableDelayedExpansion
set "PYTHONIOENCODING=utf-8"
call "%~dp0_refresh_path.bat"
cd /d "%~dp0\.."
title GPM Workbench Python Doctor
echo.

echo === PATH ^(gekuerzt^) ===
echo %PATH:~0,200%...
echo.

echo === where py / python ===
where py 2>nul || echo py: nicht gefunden
where python 2>nul || echo python: nicht gefunden
echo.

echo === py -0p ===
py -0p 2>nul || echo py -0p: nicht verfuegbar
echo.

echo === _resolve_python.bat ===
set "_FOUND="
for /f "usebackq delims=" %%P in (`call "%~dp0_resolve_python.bat" 2^>nul`) do (
    echo [OK] %%P
    set "_FOUND=1"
)
if not defined _FOUND echo [MISS] Kein venv-faehiger Interpreter gefunden
echo.

echo === find_python.py --doctor ===
set "_PROBE="
where py >nul 2>&1
if !errorlevel! equ 0 set "_PROBE=py -3"
if not defined _PROBE (
    where python >nul 2>&1
    if !errorlevel! equ 0 set "_PROBE=python"
)
if defined _PROBE (
    !_PROBE! "%~dp0find_python.py" --doctor
) else (
    echo Kein Python-Launcher fuer detaillierte Diagnose.
    echo Installieren Sie Python von https://www.python.org/downloads/
)

echo.
pause
