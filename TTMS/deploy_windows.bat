@echo off
REM Windows Deployment Helper Script for TTMS
REM This script helps setup and run TTMS on Windows servers

setlocal enabledelayedexpansion

echo.
echo ========================================
echo TTMS Production Deployment Helper
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo [!] .env file not found!
    echo [*] Creating .env from .env.example...
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo [+] .env created. Please edit it with your credentials.
        echo [!] Edit .env with your database credentials before continuing.
        pause
    ) else (
        echo [ERROR] .env.example not found!
        exit /b 1
    )
)

echo [+] .env file found
echo.

REM Check Python
echo [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Install Python 3.7+ and try again.
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VERSION=%%i
echo [+] Python %PY_VERSION% found

echo.
echo [*] Installing dependencies...
pip install -r backend\requirement.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    exit /b 1
)
echo [+] Dependencies installed

echo.
echo [*] Testing database connection...
python -c "import os; from dotenv import load_dotenv; import pymysql; load_dotenv(); conn = pymysql.connect(host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')); print('[+] Database connection OK'); conn.close()" 
if errorlevel 1 (
    echo [ERROR] Could not connect to database!
    echo Please verify your .env credentials
    pause
    exit /b 1
)

echo.
echo ========================================
echo Ready to Deploy!
echo ========================================
echo.
echo Choose deployment method:
echo.
echo 1. Waitress (Recommended for Windows)
echo 2. Gunicorn (Linux/WSL only)
echo 3. Flask Development Server (Testing only)
echo 4. Exit
echo.

set /p CHOICE="Enter your choice (1-4): "

if "%CHOICE%"=="1" (
    echo.
    echo [*] Installing Waitress...
    pip install waitress >nul 2>&1
    echo.
    echo [*] Starting TTMS with Waitress on http://0.0.0.0:8000
    echo [*] Press Ctrl+C to stop the server
    echo.
    waitress-serve --host=0.0.0.0 --port=8000 --threads=4 backend.app:app
) else if "%CHOICE%"=="2" (
    echo.
    echo [*] Installing Gunicorn...
    pip install gunicorn >nul 2>&1
    echo.
    echo [*] Starting TTMS with Gunicorn on http://0.0.0.0:8000
    echo [*] Press Ctrl+C to stop the server
    echo.
    gunicorn --workers 4 --bind 0.0.0.0:8000 backend.app:app
) else if "%CHOICE%"=="3" (
    echo.
    echo [WARNING] Development mode - not suitable for production!
    echo [*] Starting TTMS in development mode on http://127.0.0.1:5000
    echo [*] Press Ctrl+C to stop the server
    echo.
    set FLASK_ENV=development
    python backend\app.py
) else (
    echo.
    echo Exiting without starting server.
    echo.
    echo To start manually:
    echo   - Waitress: waitress-serve --host=0.0.0.0 --port=8000 backend.app:app
    echo   - Gunicorn: gunicorn --workers 4 --bind 0.0.0.0:8000 backend.app:app
    echo   - Flask:    python backend\app.py
    echo.
)

pause
