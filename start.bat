@echo off
echo Starting Hospital Appointment Booking System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing dependencies...
pip install -r requirements.txt

REM Start FastAPI server in background
echo Starting FastAPI server...
start "FastAPI Server" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for server to start
timeout /t 3 /nobreak >nul

REM Start Streamlit app
echo Starting Streamlit app...
streamlit run streamlit_app.py

pause
