@echo off
cd /d "%~dp0"

set "PY_CMD="
where python >nul 2>nul && set "PY_CMD=python"
if not defined PY_CMD where py >nul 2>nul && set "PY_CMD=py"

if not defined PY_CMD (
    echo ERROR: No se encontró Python en el PATH ^(ni "python" ni "py"^).
    echo Instálalo desde https://www.python.org/ marcando "Add python.exe to PATH".
    pause
    exit /b 1
)

for /f "delims=" %%v in ('%PY_CMD% -c "from bajador_yt import __version__; print(__version__)"') do set "APP_VERSION=%%v"
title Bajador YT v%APP_VERSION%
echo Bajador YT v%APP_VERSION%
echo.

%PY_CMD% app.py
if errorlevel 1 (
    echo.
    echo La aplicación terminó con un error. Revisa los mensajes anteriores.
    pause
)
