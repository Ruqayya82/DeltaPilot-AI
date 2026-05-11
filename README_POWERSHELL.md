# Trading App Setup Guide for PowerShell

## Prerequisites

### Windows PowerShell Setup

1. **Python Installation**
   - Download from: https://www.python.org/downloads/
   - IMPORTANT: Check "Add Python to PATH" during installation
   - Verify with:
     ```powershell
     python --version
     pip --version
     ```

2. **Node.js and npm**
   - Download from: https://nodejs.org/
   - Verify with:
     ```powershell
     node --version
     npm --version
     ```

## Running the Application

### PowerShell Setup Script
```powershell
.\setup.ps1
```

### Manual Setup Steps

#### Backend Setup
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

#### Frontend Setup
```powershell
cd frontend
npm install
npm start
```

## Application Features
- Stock symbol search
- Kronos-mini prediction integration
- Demo trading account
- Error handling and logging

## Ports
- Backend: http://localhost:5000
- Frontend: http://localhost:3000

## Troubleshooting
- Ensure ports 3000 and 5000 are available
- Check console for any error messages
- Verify all dependencies are installed

### Common Issues
- Python/npm not in PATH
- Firewall blocking local servers
- Conflicting port usage