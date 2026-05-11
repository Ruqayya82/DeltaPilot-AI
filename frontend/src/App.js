import React, { useState, useEffect } from 'react';
import './App.css';
import ReactApexChart from 'react-apexcharts';

function App() {
  const [stockSymbol, setStockSymbol] = useState('');
  const [stockData, setStockData] = useState(null);
  const [timeframe, setTimeframe] = useState('1d');
  const [balance, setBalance] = useState(10000);
  const [positions, setPositions] = useState([]);
  const [tradeQuantity, setTradeQuantity] = useState(1);
  const [tradeAction, setTradeAction] = useState('buy');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch initial account data
  useEffect(() => {
    updateBalance(0); // Just to get the current balance
    fetchPositions(); // Get current positions
  }, []);
  
  // Fetch positions
  const fetchPositions = async () => {
    try {
      const response = await fetch('http://localhost:5000/positions');
      const data = await response.json();
      
      if (response.ok) {
        setPositions(data.positions);
      }
    } catch (error) {
      console.error('Error fetching positions:', error);
    }
  };

  const fetchStockData = async () => {
    if (!stockSymbol) {
      setError('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/stock/${stockSymbol}?timeframe=${timeframe}`);
      const data = await response.json();

      if (response.ok) {
        setStockData(data);
        setError(null);
      } else {
        setError(data.error || 'Failed to fetch stock data');
        setStockData(null);
      }
    } catch (error) {
      console.error('Error fetching stock data:', error);
      setError('Network error. Please try again.');
      setStockData(null);
    } finally {
      setLoading(false);
    }
  };

  const executeTrade = async () => {
    if (!stockData) {
      setError('Please search for a stock first');
      return;
    }

    if (tradeQuantity <= 0) {
      setError('Please enter a valid quantity');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/trade/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: stockSymbol,
          quantity: parseInt(tradeQuantity),
          price: stockData.price,
          action: tradeAction // 'buy' or 'sell'
        })
      });
      const result = await response.json();
      
      if (result.success) {
        setBalance(result.balance);
        setPositions(result.positions);
        setError(null);
      } else {
        setError(result.message);
      }
    } catch (error) {
      console.error('Error executing trade:', error);
      setError('Failed to execute trade. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const closePosition = async (symbol, price, quantity = null) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/trade/close', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: symbol,
          quantity: quantity, // null will close entire position
          current_price: price
        })
      });
      const result = await response.json();
      
      if (result.success) {
        setBalance(result.balance);
        setPositions(result.positions);
        setError(null);
      } else {
        setError(result.message);
      }
    } catch (error) {
      console.error('Error closing position:', error);
      setError('Failed to close position. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const updateBalance = async (amount, reset = false) => {
    try {
      const response = await fetch('http://localhost:5000/account/balance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount, reset })
      });
      const result = await response.json();
      setBalance(result.balance);
      
      if (reset) {
        setPositions(result.positions || []);
      }
      
      setError(null);
    } catch (error) {
      console.error('Error updating balance:', error);
      setError('Failed to update balance. Please try again.');
    }
  };
  
  // Calculate current value and P&L for a position
  const calculatePositionValue = (position, currentPrice) => {
    if (!stockData || stockData.symbol !== position.symbol) {
      return {
        currentValue: position.quantity * position.avg_price,
        pnl: 0,
        pnlPercent: 0
      };
    }
    
    const currentValue = Math.abs(position.quantity) * currentPrice;
    const isShort = position.quantity < 0;
    
    // For long positions: (current - cost)
    // For short positions: (cost - current)
    const pnl = isShort 
      ? Math.abs(position.total_cost) - currentValue 
      : currentValue - Math.abs(position.total_cost);
      
    const pnlPercent = (pnl / Math.abs(position.total_cost)) * 100;
    
    return {
      currentValue,
      pnl,
      pnlPercent
    };
  };

  // Get candlestick chart options
  const getCandlestickOptions = () => {
    return {
      chart: {
        type: 'candlestick',
        height: 350,
        toolbar: {
          show: true,
          tools: {
            download: true,
            selection: true,
            zoom: true,
            zoomin: true,
            zoomout: true,
            pan: true,
          }
        },
        background: 'transparent'
      },
      theme: {
        mode: 'dark'
      },
      title: {
        text: `${stockData?.symbol || 'Stock'} Candlestick Chart (${getTimeframeLabel()})`,
        align: 'left',
        style: {
          color: '#e1e1e1'
        }
      },
      xaxis: {
        type: 'datetime',
        labels: {
          style: {
            colors: '#e1e1e1'
          }
        }
      },
      yaxis: {
        tooltip: {
          enabled: true
        },
        labels: {
          style: {
            colors: '#e1e1e1'
          }
        }
      },
      tooltip: {
        theme: 'dark'
      },
      plotOptions: {
        candlestick: {
          colors: {
            upward: '#4caf50',
            downward: '#f44336'
          }
        }
      }
    };
  };

  // Prepare prediction chart options
  const getPredictionChartOptions = () => {
    return {
      chart: {
        type: 'bar',
        height: 200,
        background: 'transparent',
      },
      plotOptions: {
        bar: {
          horizontal: false,
          columnWidth: '70%',
        }
      },
      colors: ['#FFD700', '#4caf50', '#2196F3', '#f44336', '#9C27B0'],
      title: {
        text: 'Price Predictions',
        align: 'left',
        style: {
          color: '#e1e1e1'
        }
      },
      theme: {
        mode: 'dark'
      },
      xaxis: {
        categories: ['Current', 'Pred Close', 'Pred High', 'Pred Low', 'Pred Open'],
        labels: {
          style: {
            colors: '#e1e1e1'
          }
        }
      },
      yaxis: {
        labels: {
          formatter: (value) => `$${value.toFixed(2)}`,
          style: {
            colors: '#e1e1e1'
          }
        }
      },
      tooltip: {
        y: {
          formatter: (value) => `$${value.toFixed(2)}`
        },
        theme: 'dark'
      }
    };
  };

  // Helper function to get a user-friendly label for timeframes
  const getTimeframeLabel = () => {
    const labels = {
      '5m': '5 Minutes',
      '1h': '1 Hour',
      '1d': 'Daily'
    };
    return labels[timeframe] || 'Daily';
  };

  return (
    <div className="App">
      <header className="App-header">
        <img 
          src="/images/trading_app_logo.png" 
          alt="DeltaPilot Logo" 
          style={{ 
            position: 'absolute', 
            left: '20px', 
            top: '20px', 
            height: '50px',
            filter: 'drop-shadow(2px 2px 2px rgba(0,0,0,0.5))'
          }} 
        />
        <h1>Trading App with Kronos-mini Predictions</h1>
      </header>
      
      {error && <div className="error-message">{error}</div>}

      <div className="trading-layout">
        <div className="main-panel">
          <div className="panel">
              <h2>Stock Search</h2>
              <div className="stock-search">
                <input 
                  type="text" 
                  value={stockSymbol} 
                  onChange={(e) => setStockSymbol(e.target.value.toUpperCase())}
                  placeholder="Enter Stock Symbol (e.g., AAPL, MSFT, GOOGL)"
                />
                <button 
                  className="primary-button" 
                  onClick={fetchStockData}
                  disabled={loading}
                >
                  {loading ? 'Loading...' : 'Search Stock'}
                </button>
              </div>
              
              <div className="timeframe-selector">
                <label>Timeframe:</label>
                <div className="button-group">
                  <button 
                    className={timeframe === '5m' ? 'primary-button' : ''}
                    onClick={() => {
                      setTimeframe('5m');
                      if (stockData) fetchStockData();
                    }}
                  >
                    5 Min
                  </button>
                  <button 
                    className={timeframe === '1h' ? 'primary-button' : ''}
                    onClick={() => {
                      setTimeframe('1h');
                      if (stockData) fetchStockData();
                    }}
                  >
                    1 Hour
                  </button>
                  <button 
                    className={timeframe === '1d' ? 'primary-button' : ''}
                    onClick={() => {
                      setTimeframe('1d');
                      if (stockData) fetchStockData();
                    }}
                  >
                    Daily
                  </button>
                </div>
              </div>
          </div>

          {stockData && (
            <div className="panel">
              <h2>{stockData.name || stockData.symbol} Stock Details</h2>
              <div className="balance-display">
                ${stockData.price.toFixed(2)} <span style={{fontSize: '1rem', color: 'gray'}}>per share</span>
              </div>
              
              <div className="chart-container">
                {stockData.candle_data && (
                  <ReactApexChart
                    options={getCandlestickOptions()}
                    series={[{ data: stockData.candle_data }]}
                    type="candlestick"
                    height={350}
                  />
                )}
              </div>
              
              <div className="prediction-container">
                <h3>Kronos-mini Prediction</h3>
                <p>Our AI model predicts the following values for the next trading period:</p>
                
                <div className="prediction-section">
                  <h4>Kronos Model Stock Price Predictions</h4>
                  <p className="token-explanation">These are the actual predicted price values in dollars for {stockData.symbol}</p>
                  <div className="prediction-value">
                    <div className="prediction-item">
                      <span className="prediction-label">Predicted Close</span>
                      <span className="prediction-number">${stockData.prediction[0].toFixed(2)}</span>
                    </div>
                    <div className="prediction-item">
                      <span className="prediction-label">Predicted High</span>
                      <span className="prediction-number">${stockData.prediction[1].toFixed(2)}</span>
                    </div>
                    <div className="prediction-item">
                      <span className="prediction-label">Predicted Low</span>
                      <span className="prediction-number">${stockData.prediction[2].toFixed(2)}</span>
                    </div>
                    <div className="prediction-item">
                      <span className="prediction-label">Predicted Open</span>
                      <span className="prediction-number">${stockData.prediction[3].toFixed(2)}</span>
                    </div>
                  </div>
                  
                  <h4>Current Price Comparison</h4>
                  <p className="token-explanation">How the predictions compare to the current price</p>
                  <div className="prediction-value token-values">
                    <div className="prediction-item">
                      <span className="prediction-label">Current Price</span>
                      <span className="prediction-number">${stockData.price.toFixed(2)}</span>
                    </div>
                    <div className="prediction-item">
                      <span className="prediction-label">Price Change</span>
                      <span className="prediction-number" style={{color: stockData.prediction[0] > stockData.price ? '#4caf50' : '#f44336'}}>
                        ${(stockData.prediction[0] - stockData.price).toFixed(2)}
                      </span>
                      <span className="token-percent">
                        ({((stockData.prediction[0] / stockData.price - 1) * 100).toFixed(2)}%)
                      </span>
                    </div>
                    <div className="prediction-item">
                      <span className="prediction-label">Predicted Volatility</span>
                      <span className="prediction-number">${(stockData.prediction[1] - stockData.prediction[2]).toFixed(2)}</span>
                      <span className="token-percent">
                        ({((stockData.prediction[1] - stockData.prediction[2]) / stockData.price * 100).toFixed(2)}%)
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="chart-container" style={{ height: '200px', marginTop: '20px' }}>
                  {stockData.prediction && (
                    <ReactApexChart
                      options={getPredictionChartOptions()}
                      series={[
                        {
                          name: "Price",
                          data: [
                            stockData.price,
                            stockData.prediction[0], // Close
                            stockData.prediction[1], // High
                            stockData.prediction[2], // Low
                            stockData.prediction[3]  // Open
                          ]
                        }
                      ]}
                      type="bar"
                      height={200}
                    />
                  )}
                </div>
              </div>
              
              <div className="trade-section">
                <div className="trade-controls">
                  <input 
                    type="number" 
                    value={tradeQuantity}
                    onChange={(e) => setTradeQuantity(Number(e.target.value))}
                    placeholder="Quantity"
                    min="1"
                  />
                  <div className="trade-action-buttons">
                    <button 
                      className={`${tradeAction === 'buy' ? 'primary-button' : ''}`}
                      onClick={() => setTradeAction('buy')}
                    >
                      Buy
                    </button>
                    <button 
                      className={`${tradeAction === 'sell' ? 'secondary-button' : ''}`}
                      onClick={() => setTradeAction('sell')}
                    >
                      Sell
                    </button>
                  </div>
                </div>
                <button 
                  className={tradeAction === 'buy' ? 'primary-button' : 'secondary-button'} 
                  onClick={executeTrade}
                  disabled={loading}
                >
                  {tradeAction === 'buy' ? 'Buy' : 'Sell'} {tradeQuantity} Shares (${(tradeQuantity * stockData.price).toFixed(2)})
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="side-panel">
          <div className="account-section">
            <h2>Demo Account</h2>
            <div className="balance-display">${balance.toFixed(2)}</div>
            <div className="button-group">
              <button className="primary-button" onClick={() => updateBalance(1000)}>
                Add $1000
              </button>
              <button className="secondary-button" onClick={() => updateBalance(-1000)}>
                Withdraw $1000
              </button>
              <button className="reset-button" onClick={() => updateBalance(0, true)}>
                Reset Account
              </button>
            </div>
          </div>
          
          <div className="panel">
            <h2>Open Positions</h2>
            {positions.length === 0 ? (
              <p>No open positions. Search for a stock to trade.</p>
            ) : (
              <div className="positions-list">
                {positions.map((position, index) => {
                  const posInfo = calculatePositionValue(position, 
                    stockData && stockData.symbol === position.symbol ? stockData.price : position.avg_price);
                  
                  const isShort = position.quantity < 0;
                  const posType = isShort ? 'Short' : 'Long';
                  const isProfitable = posInfo.pnl > 0;
                  
                  return (
                    <div key={index} className="position-item panel" style={{marginBottom: '10px', padding: '10px'}}>
                      <div className="position-header">
                        <strong>{position.symbol}</strong>
                        <span className={`position-type ${isShort ? 'short' : 'long'}`}>
                          {posType}
                        </span>
                      </div>
                      
                      <div className="position-details">
                        <div>
                          {Math.abs(position.quantity)} shares @ ${position.avg_price.toFixed(2)}
                        </div>
                        
                        <div className="position-value">
                          <div>Cost: <strong>${Math.abs(position.total_cost).toFixed(2)}</strong></div>
                          <div>Value: <strong>${posInfo.currentValue.toFixed(2)}</strong></div>
                        </div>
                        
                        <div className={`position-pnl ${isProfitable ? 'profit' : 'loss'}`}>
                          P&L: <strong>${posInfo.pnl.toFixed(2)} ({posInfo.pnlPercent.toFixed(2)}%)</strong>
                        </div>
                      </div>
                      
                      {stockData && stockData.symbol === position.symbol && (
                        <div className="position-actions">
                          <button 
                            className="close-position-button" 
                            onClick={() => closePosition(position.symbol, stockData.price)}
                          >
                            Close Position
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;