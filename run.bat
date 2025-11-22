@echo off
cd /d "%~dp0"

:: Check for permissions
NET SESSION >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Starting Wispr Flow Clone...
python main.py
pause