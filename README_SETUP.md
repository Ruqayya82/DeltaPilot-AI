# Trading App Setup Guide

## Prerequisites

### Windows
1. **Python**
   - Download from: https://www.python.org/downloads/
   - IMPORTANT: Check "Add Python to PATH" during installation
   - Verify installation: 
     ```
     python --version
     pip --version
     ```

2. **Node.js and npm**
   - Download from: https://nodejs.org/
   - Verify installation:
     ```
     node --version
     npm --version
     ```

### Troubleshooting

#### Python Path Issues
- Open System Properties > Advanced > Environment Variables
- Edit "Path" variable
- Add Python installation directory (e.g., `C:\Python313`)
- Add Python Scripts directory (e.g., `C:\Python313\Scripts`)

#### npm Not Recognized
- Reinstall Node.js
- Ensure "Add to PATH" is selected during installation
- Restart terminal/IDE

## Setup Methods

### Windows Command Prompt / PowerShell
```bash
cd trading_app
setup.bat
```

### Git Bash
```bash
cd trading_app
bash setup_gitbash.sh
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