@echo off
echo ========================================================
echo   Starting Digital Legacy Vault - DA3 Backend & Frontend
echo ========================================================

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

echo Starting FastAPI server with Uvicorn...
python run.py
pause
