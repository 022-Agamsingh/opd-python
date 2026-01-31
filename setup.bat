@echo off
echo ============================================
echo OPD Token System - Python Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Python found!
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Dependencies installed!
echo.

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file with your MongoDB URI
    echo.
)

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env file with your MongoDB URI
echo 2. Run: python main.py
echo 3. Visit: http://localhost:8000/docs
echo.
echo To run simulation: python simulation.py
echo.
pause
