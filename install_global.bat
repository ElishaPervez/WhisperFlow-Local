@echo off
setlocal EnableDelayedExpansion

echo ===================================================
echo Wispr Flow Clone - Global Installation
echo ===================================================
echo.
echo This script will install all dependencies GLOBALLY
echo (not in a virtual environment).
echo.
echo Press Ctrl+C to cancel, or
pause

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM Check Python version (must be 3.11 or 3.12)
echo Checking Python version...
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo Detected Python %PYTHON_VERSION%

echo %PYTHON_VERSION% | findstr "^3.11" >nul
if %errorlevel% equ 0 goto :version_ok

echo %PYTHON_VERSION% | findstr "^3.12" >nul
if %errorlevel% equ 0 goto :version_ok

echo %PYTHON_VERSION% | findstr "^3.13" >nul
if %errorlevel% equ 0 goto :version_ok

echo.
echo [!] WARNING: Python %PYTHON_VERSION% detected.
echo [!] This version may not be supported by all dependencies.
echo [!] Recommended: Python 3.11 or 3.12
echo [!] Current issues: onnxruntime (required by faster-whisper) has no wheels for Python 3.14+
echo.
echo Press Ctrl+C to cancel, or
pause
echo Continuing anyway...
echo.

:version_ok

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM GPU Detection Logic for RTX 50 Series (Blackwell)
echo.
echo ===================================================
echo Checking for NVIDIA GPU and CUDA version...
echo ===================================================

set "RTX50_DETECTED=0"

REM Check using nvidia-smi if available
where nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    REM Check Compute Capability (sm_120 is reported as 12.0)
    for /f "tokens=*" %%i in ('nvidia-smi --query-gpu=compute_cap --format=csv^,noheader') do (
        set "COMPUTE_CAP=%%i"
        echo Detected Compute Capability: !COMPUTE_CAP!

        REM Check if starts with 12.
        echo !COMPUTE_CAP! | findstr "^12\." >nul
        if !errorlevel! equ 0 (
            echo [!] Compute Capability 12.x detected ^(Blackwell/RTX 50^).
            set RTX50_DETECTED=1
        )
    )

    REM Check CUDA Version (Fallback/Confirmation)
    nvidia-smi | findstr "CUDA Version: 12.8" >nul
    if !errorlevel! equ 0 set RTX50_DETECTED=1

    nvidia-smi | findstr "CUDA Version: 12.9" >nul
    if !errorlevel! equ 0 set RTX50_DETECTED=1

    nvidia-smi | findstr "CUDA Version: 13" >nul
    if !errorlevel! equ 0 set RTX50_DETECTED=1

) else (
    echo nvidia-smi not found. Assuming standard installation.
)

echo.
echo ===================================================
echo Installing PyTorch
echo ===================================================

if "!RTX50_DETECTED!"=="1" (
    echo.
    echo [!] RTX 50 Series / CUDA 12.8+ Detected!
    echo [!] Installing PyTorch Nightly for sm_120 support...
    echo [!] Command: pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
    echo.
    python -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
) else (
    echo.
    echo [i] Standard GPU or CPU detected.
    echo [i] Installing stable PyTorch with CUDA 12.1...
    echo.
    python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
)

echo.
echo ===================================================
echo Installing Core Dependencies
echo ===================================================
echo.
python -m pip install PyQt6
python -m pip install faster-whisper
python -m pip install sounddevice
python -m pip install numpy
python -m pip install keyboard
python -m pip install pywin32
python -m pip install scipy
python -m pip install pyinstaller
python -m pip install google-generativeai
python -m pip install fastapi
python -m pip install uvicorn
python -m pip install jinja2
python -m pip install python-multipart

echo.
echo ===================================================
echo Ensuring Runtime Stability
echo ===================================================
echo (Fixing common DLL errors)
echo.
python -m pip install --force-reinstall intel-openmp numpy

echo.
echo ===================================================
echo Global Installation Complete!
echo ===================================================
echo.
echo All dependencies are now installed globally.
echo You can now run the application with:
echo     python main.py
echo.
echo Or create a simple run script.
echo ===================================================
pause
