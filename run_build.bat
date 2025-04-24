@echo off
echo [INFO] Starting Python build script...

cd /d %~dp0

REM Check if Python exists
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found. Please check PATH settings.
    exit /b 1
)

python main.py

echo [INFO] Python build finished.
