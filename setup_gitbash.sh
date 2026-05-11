#!/bin/bash

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Prerequisite check function
check_prereq() {
    local cmd=$1
    local install_hint=$2
    if ! command -v "$cmd" &> /dev/null; then
        echo -e "${RED}Error: $cmd is not installed.${NC}"
        echo -e "${YELLOW}Please install $cmd:${NC}"
        echo "$install_hint"
        exit 1
    fi
}

# Check Python
check_prereq python "Download from https://www.python.org/downloads/"

# Check pip
check_prereq pip "Run: python -m ensurepip --upgrade"

# Check npm
check_prereq npm "Download Node.js from https://nodejs.org/"

# Create virtual environment
echo -e "${GREEN}Creating Python virtual environment...${NC}"
python -m venv backend/venv

# Activate virtual environment and install dependencies
source backend/venv/Scripts/activate
echo -e "${GREEN}Installing backend dependencies...${NC}"
pip install -r backend/requirements.txt

# Start backend server
echo -e "${GREEN}Starting backend server...${NC}"
python backend/app.py &
BACKEND_PID=$!

# Change to frontend directory
cd frontend

# Install frontend dependencies
echo -e "${GREEN}Installing frontend dependencies...${NC}"
npm install

# Start frontend server
echo -e "${GREEN}Starting frontend server...${NC}"
npm start &
FRONTEND_PID=$!

# Trap to kill background processes on script exit
trap 'kill $BACKEND_PID $FRONTEND_PID' EXIT

echo -e "${GREEN}Setup complete!${NC}"
echo -e "Backend: ${YELLOW}http://localhost:5000${NC}"
echo -e "Frontend: ${YELLOW}http://localhost:3000${NC}"

# Wait for user input to keep script running
read -p "Press Enter to stop the application..."