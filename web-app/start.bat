@echo off
REM Voss Taxi Web App Startup Script for Windows

echo Starting Voss Taxi Web App...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed
    pause
    exit /b 1
)

REM Start backend
echo Starting backend server...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Installing backend dependencies...
pip install -q -r requirements.txt

REM Start backend in new window
echo Starting FastAPI server on port 8000...
start "Voss Taxi Backend" cmd /k "uvicorn main:app --host 0.0.0.0 --port 8000"

cd ..

REM Start frontend
echo.
echo Starting frontend server...
cd frontend

REM Install dependencies
echo Installing frontend dependencies...
call npm install

REM Start frontend in new window
echo Starting React dev server on port 3000...
start "Voss Taxi Frontend" cmd /k "npm run dev"

cd ..

echo.
echo =========================================
echo Voss Taxi Web App is running!
echo =========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Close the terminal windows to stop the servers
echo.
pause
