@echo off
cd /d "%~dp0"
REM ========================================================================
REM Quick Start Script for Forensic Analysis Tool
REM Automatically sets up environment and runs the tool
REM ========================================================================

echo.
echo ========================================================================
echo           FORENSIC ANALYSIS TOOL - QUICK START
echo ========================================================================
echo.

REM Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with Administrator privileges
) else (
    echo [ERROR] This script requires Administrator privileges!
    echo Please right-click and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo.
echo [STEP 1/5] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Python is installed
    python --version
) else (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org
    echo.
    pause
    exit /b 1
)

echo.
echo [STEP 2/5] Checking virtual environment...
if exist "venv\" (
    echo [OK] Virtual environment exists
) else (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %errorLevel% == 0 (
        echo [OK] Virtual environment created
    ) else (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo.
echo [STEP 3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorLevel% == 0 (
    echo [OK] Virtual environment activated
) else (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo [STEP 4/5] Installing dependencies...
pip install -r requirements.txt --quiet
if %errorLevel% == 0 (
    echo [OK] Dependencies installed
) else (
    echo [WARNING] Some dependencies may have failed to install
    echo Attempting to continue...
)

echo.
echo [STEP 5/5] Running Forensic Analysis Tool...
echo.
echo ========================================================================
echo.

python src\forensic_master.py

echo.
echo ========================================================================
echo                      EXECUTION COMPLETED
echo ========================================================================
echo.
echo Check the following directories for output:
echo   - Reports: output\reports\master\
echo   - Artifacts: output\artifacts\
echo   - Logs: output\logs\
echo.
pause