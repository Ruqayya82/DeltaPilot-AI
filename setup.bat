@echo off
echo Setting up Trading App with Kronos-mini Predictions

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    exit /b 1
)

REM Check pip installation
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed.
    python -m ensurepip --upgrade
)

REM Check npm installation
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo npm is not installed.
    echo Please install Node.js from https://nodejs.org/
    exit /b 1
)

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv backend\venv

REM Activate virtual environment and install backend dependencies
call backend\venv\Scripts\activate && (
    echo Installing backend dependencies...
    pip install -r backend\requirements.txt
    
    REM Start backend server in a separate window
    start cmd /c "cd backend && venv\Scripts\activate && python app.py"
)

REM Install frontend dependencies and start frontend
cd frontend
echo Installing frontend dependencies...
npm install
start cmd /c "npm start"

echo Setup complete. Backend and frontend servers are starting.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000