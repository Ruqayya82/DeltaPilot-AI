# Trading App with Kronos-mini Predictions

## Overview
A trading application that uses the Kronos-mini model to provide stock predictions and allows users to manage a demo trading account.

## Features
- Stock search and data retrieval
- Kronos-mini prediction integration
- Demo account with balance management
- Trade opening and closing functionality

## Prerequisites
- Python 3.8+
- Node.js 14+
- pip
- npm

## Setup

### Backend Setup
1. Navigate to the backend directory
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### Frontend Setup
1. Navigate to the frontend directory
```bash
cd frontend
npm install
```

## Running the Application

### Start Backend
```bash
cd backend
python app.py
```

### Start Frontend
```bash
cd frontend
npm start
```

## Technologies Used
- Backend: Python, Flask, yfinance
- Frontend: React
- Machine Learning: Kronos-mini model