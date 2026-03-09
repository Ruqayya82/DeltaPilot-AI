# DeltaPilot AI

DeltaPilot AI is a stock market analysis and signal generation platform designed to provide real-time market data and algorithmic trading insights. The system uses a custom backend API to retrieve live stock prices and will eventually generate intelligent trading signals to assist users in making informed investment decisions.

## Project Overview

DeltaPilot AI combines financial market data with algorithmic analysis to create a lightweight platform for monitoring stock prices and generating trading signals. The backend system retrieves real-time stock information from external APIs and processes it for use in a user-facing dashboard.

This project demonstrates concepts in:

- Backend API development
- Financial data integration
- Algorithmic signal generation
- Software architecture and project planning

## Features

- Real-time stock price retrieval
- REST API for market data
- Modular backend architecture
- Environment-based API key security
- Expandable system for trading signal algorithms

Planned Features:

- Trading signal engine
- Interactive frontend dashboard
- Stock watchlists
- Historical data analysis
- Market alerts and notifications

## Technology Stack

Backend:
- Node.js
- Express.js
- Axios
- Dotenv

External API:
- Alpaca Market Data API

Development Tools:
- Visual Studio Code
- Git
- GitHub

Design Tools:
- Figma

## Project Structure

```

DeltaPilot-AI
│
├ backend
│   ├ routes
│   │   └ market.js
│   ├ server.js
│   ├ package.json
│
├ frontend
│
├ .gitignore
└ README.md

```

## API Endpoint Example

Retrieve the latest stock price:

```

GET /api/market/price/:symbol

```

Example:

```

[http://localhost:5000/api/market/price/AAPL](http://localhost:5000/api/market/price/AAPL)

```

Example Response:

```

{
"symbol": "AAPL",
"price": 189.42
}

```

## Setup Instructions

### 1. Clone the Repository

```

git clone [https://github.com/YOUR_USERNAME/DeltaPilot-AI.git](https://github.com/YOUR_USERNAME/DeltaPilot-AI.git)

```

### 2. Navigate to Backend

```

cd backend

```

### 3. Install Dependencies

```

npm install

```

### 4. Create Environment File

Create a `.env` file inside the backend folder.

Example:

```

PORT=5000
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key

```

### 5. Run the Server

```

npm start

```

The backend will run at:

```

[http://localhost:5000](http://localhost:5000)

```

## Development Status

Current Progress:

- Project architecture created
- Backend server implemented
- Market data API integration complete
- Initial testing and debugging completed

In Progress:

- Trading signal engine
- Frontend interface

## Future Improvements

- AI-powered trading signals
- Real-time chart visualization
- User authentication
- Portfolio tracking
- Deployment to cloud infrastructure

## Learning Objectives

This project was created to explore:

- Financial data APIs
- Backend development with Node.js
- RESTful API design
- Software project organization
- Version control with Git

## Author

Ruqayya Mustafa

## License

This project was created for CISC. 4905 and CUNY Tech Prep
