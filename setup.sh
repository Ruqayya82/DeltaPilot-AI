#!/bin/bash

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed."
    exit 1
fi

# Check pip installation
if ! command -v pip3 &> /dev/null; then
    echo "pip is not installed."
    exit 1
fi

# Check npm installation
if ! command -v npm &> /dev/null; then
    echo "npm is not installed."
    exit 1
fi

# Create virtual environment
python3 -m venv backend/venv

# Activate virtual environment and install dependencies
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# Start backend server in background
python3 backend/app.py &
BACKEND_PID=$!

# Install frontend dependencies
cd frontend
npm install

# Start frontend server
npm start &
FRONTEND_PID=$!

# Trap to kill background processes on script exit
trap 'kill $BACKEND_PID $FRONTEND_PID' EXIT

echo "Setup complete. Backend and frontend servers are running."
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"

# Wait for user input to keep script running
read -p "Press Enter to stop the application..."