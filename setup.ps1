# Trading App Setup Script for PowerShell

# Enable verbose output and stop on first error
$ErrorActionPreference = 'Stop'

# Function to check and install dependencies
function Check-Dependency {
    param (
        [string]$Command,
        [string]$InstallInstructions
    )

    try {
        Invoke-Expression "$Command --version" | Out-Null
        Write-Host "$Command is installed." -ForegroundColor Green
    }
    catch {
        Write-Host "$Command is not installed." -ForegroundColor Red
        Write-Host "Installation Instructions:" -ForegroundColor Yellow
        Write-Host $InstallInstructions -ForegroundColor Yellow
        throw "Dependency not found: $Command"
    }
}

# Dependency Checks
Write-Host "Checking System Dependencies..." -ForegroundColor Cyan

try {
    Check-Dependency "python" "Download from https://www.python.org/downloads/"
    Check-Dependency "pip" "Run: python -m ensurepip --upgrade"
    Check-Dependency "node" "Download from https://nodejs.org/"
    Check-Dependency "npm" "Comes with Node.js installation"
}
catch {
    Write-Host "Dependency check failed. Please install missing components." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "Creating Python Virtual Environment..." -ForegroundColor Green
python -m venv backend\venv

# Activate virtual environment and install dependencies
Write-Host "Installing Backend Dependencies..." -ForegroundColor Green
.\backend\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt

# Prepare to start servers
$BackendScript = {
    Set-Location backend
    .\venv\Scripts\Activate.ps1
    python app.py
}

$FrontendScript = {
    Set-Location frontend
    npm install
    npm start
}

# Start backend in a new window
Start-Process powershell -ArgumentList "-Command", $BackendScript -NoNewWindow

# Small delay to ensure backend starts
Start-Sleep -Seconds 2

# Start frontend in a new window
Start-Process powershell -ArgumentList "-Command", $FrontendScript -NoNewWindow

# Open browser
Start-Process "http://localhost:3000"

Write-Host "Trading App is now running!" -ForegroundColor Green
Write-Host "Backend: http://localhost:5000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C in each window to stop the application." -ForegroundColor Cyan

# Keep script window open
Read-Host "Press Enter to exit..."