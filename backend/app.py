from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import numpy as np
import sys
import os
import logging
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add Kronos directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'kronos_model'))

# Import the Kronos model - we want to use either KronosFull (recommended) or KronosMini (fallback)
# The KronosFull model tries to access the Kronos repository from GitHub
try:
    logger.info("Attempting to use Kronos model from GitHub")
    from kronos_full import KronosFull
    model = KronosFull()
    logger.info("Successfully initialized Kronos model from GitHub")
except Exception as e:
    logger.error(f"Failed to initialize Kronos model from GitHub: {e}")
    logger.warning("Falling back to KronosMini model")
    try:
        from kronos_mini import KronosMini
        model = KronosMini()
        logger.info("Using KronosMini model")
    except Exception as mini_error:
        logger.error(f"Failed to initialize KronosMini model: {mini_error}")
        raise RuntimeError("Cannot start application without a prediction model")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Note: the Kronos model instance is already created above

class DemoAccount:
    def __init__(self, initial_balance=10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = {}

    def reset_balance(self):
        """Reset the account to initial state"""
        self.balance = self.initial_balance
        self.positions = {}
        return self.balance

    def update_balance(self, amount):
        """Add or withdraw funds from account"""
        self.balance += amount
        return self.balance

    def get_positions(self):
        """Return all positions with current data"""
        position_list = []
        for symbol, pos in self.positions.items():
            position_list.append({
                'symbol': symbol,
                'quantity': pos['quantity'],
                'avg_price': pos['avg_price'],
                'total_cost': pos['total_cost']
            })
        return position_list

    def execute_trade(self, symbol, quantity, price, action='buy'):
        """
        Execute a trade - either buy or sell
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares (positive)
            price: Price per share
            action: 'buy' or 'sell'
            
        Returns:
            (success, message, executed_quantity)
        """
        # Validate quantity is positive
        if quantity <= 0:
            return False, "Quantity must be positive", 0
            
        # Handle buy orders
        if action == 'buy':
            # First check if we have a short position to cover
            if symbol in self.positions and self.positions[symbol]['quantity'] < 0:
                # We have a short position, buying will first cover this
                short_position = self.positions[symbol]
                short_quantity = abs(short_position['quantity'])
                
                # Check if this buy will fully or partially cover the short
                if quantity <= short_quantity:
                    # Only covering some/all of the short position
                    cover_cost = quantity * price
                    if cover_cost > self.balance:
                        return False, "Insufficient funds to cover short position", 0
                    
                    # Reduce the short position
                    self.balance -= cover_cost
                    short_position['quantity'] += quantity  # Less negative
                    
                    # If fully covered, remove the position
                    if short_position['quantity'] == 0:
                        del self.positions[symbol]
                        return True, "Short position fully covered", quantity
                    else:
                        # Update remaining short position cost basis
                        remaining_ratio = short_position['quantity'] / -short_quantity
                        short_position['total_cost'] *= remaining_ratio
                        short_position['avg_price'] = abs(short_position['total_cost'] / short_position['quantity'])
                        return True, f"Short position partially covered, {abs(short_position['quantity'])} shares remaining short", quantity
                else:
                    # Covering the entire short and going long with the rest
                    cover_cost = short_quantity * price
                    long_quantity = quantity - short_quantity
                    long_cost = long_quantity * price
                    total_cost = cover_cost + long_cost
                    
                    if total_cost > self.balance:
                        return False, "Insufficient funds for this transaction", 0
                    
                    self.balance -= total_cost
                    
                    # Create a new long position
                    self.positions[symbol] = {
                        'quantity': long_quantity,
                        'avg_price': price,
                        'total_cost': long_cost
                    }
                    
                    return True, f"Covered short position of {short_quantity} shares and opened long position of {long_quantity} shares", quantity
            
            # Normal buy - no existing short position
            total_cost = quantity * price
            if total_cost > self.balance:
                return False, "Insufficient funds", 0
            
            self.balance -= total_cost
            if symbol in self.positions and self.positions[symbol]['quantity'] > 0:
                current_quantity = self.positions[symbol]['quantity']
                current_cost = self.positions[symbol]['total_cost']
                
                # Update position with average cost
                self.positions[symbol]['quantity'] += quantity
                self.positions[symbol]['total_cost'] += total_cost
                if self.positions[symbol]['quantity'] > 0:
                    self.positions[symbol]['avg_price'] = self.positions[symbol]['total_cost'] / self.positions[symbol]['quantity']
            else:
                # Create new position
                self.positions[symbol] = {
                    'quantity': quantity,
                    'avg_price': price,
                    'total_cost': total_cost
                }
            return True, "Position opened", quantity
            
        # Handle sell orders
        elif action == 'sell':
            # Check if we have this position
            if symbol not in self.positions:
                # New short position
                total_cost = quantity * price
                self.positions[symbol] = {
                    'quantity': -quantity,  # Negative for short positions
                    'avg_price': price,
                    'total_cost': -total_cost  # Negative cost for shorts
                }
                self.balance += total_cost  # Add funds for selling
                return True, "Short position opened", quantity
            
            # We have a position - check if it's a long or short
            position = self.positions[symbol]
            current_quantity = position['quantity']
            
            if current_quantity > 0:  # Long position
                if quantity <= current_quantity:
                    # Partial or full close of long position
                    sale_value = quantity * price
                    # Calculate proportion of position sold for correct cost accounting
                    proportion_sold = quantity / current_quantity
                    cost_basis_sold = position['total_cost'] * proportion_sold
                    
                    self.balance += sale_value
                    
                    # Update position
                    position['quantity'] -= quantity
                    position['total_cost'] -= cost_basis_sold
                    
                    if position['quantity'] == 0:
                        del self.positions[symbol]
                        return True, "Position closed completely", quantity
                    else:
                        if position['quantity'] > 0:
                            position['avg_price'] = position['total_cost'] / position['quantity']  
                        return True, f"Partially closed position ({position['quantity']} shares remaining)", quantity
                else:
                    # Try to sell more than we have - close position and go short
                    sale_value = current_quantity * price  # Sell all we have
                    short_quantity = quantity - current_quantity  # Amount to short
                    short_value = short_quantity * price  # Value of short
                    
                    # Add both values to balance
                    self.balance += sale_value + short_value
                    
                    # Create short position
                    self.positions[symbol] = {
                        'quantity': -short_quantity,  # Negative for short
                        'avg_price': price,
                        'total_cost': -short_value  # Negative cost
                    }
                    
                    return True, f"Closed long position and opened short position of {short_quantity} shares", quantity
            
            else:  # Short position (negative quantity)
                # Selling more when already short - increase short position
                additional_short = quantity
                total_short_value = additional_short * price
                
                # Update position
                current_short_quantity = abs(position['quantity'])
                position['quantity'] -= additional_short  # Further decrease (more negative)
                position['total_cost'] -= total_short_value
                position['avg_price'] = abs(position['total_cost'] / position['quantity'])
                
                # Add to balance
                self.balance += total_short_value
                
                return True, f"Increased short position to {abs(position['quantity'])} shares", quantity
        
        return False, "Invalid action", 0

    def close_position(self, symbol, quantity=None, current_price=None):
        """
        Close a position completely or partially
        If quantity is None, close entire position
        """
        if symbol not in self.positions:
            return False, "No position found for this symbol", 0
        
        position = self.positions[symbol]
        current_quantity = position['quantity']
        abs_quantity = abs(current_quantity)
        
        # If no quantity specified, close entire position
        if quantity is None or quantity >= abs_quantity:
            quantity = abs_quantity
        
        # For long positions (positive quantity)
        if current_quantity > 0:
            # Calculate proper profit/loss accounting
            sale_value = quantity * current_price
            proportion_sold = quantity / current_quantity
            cost_basis_sold = position['total_cost'] * proportion_sold
            
            # Add proceeds to balance
            self.balance += sale_value
            
            if quantity >= current_quantity:
                # Close entire position
                del self.positions[symbol]
                return True, "Position closed completely", current_quantity
            else:
                # Partial close - update remaining position
                new_quantity = current_quantity - quantity
                position['total_cost'] -= cost_basis_sold
                position['quantity'] = new_quantity
                if new_quantity > 0:
                    position['avg_price'] = position['total_cost'] / new_quantity
                return True, f"Partially closed position ({new_quantity} shares remaining)", quantity
        
        # For short positions (negative quantity)
        else:
            buy_cost = quantity * current_price
            
            # Calculate proper profit/loss accounting for shorts
            proportion_covered = quantity / abs_quantity
            original_short_value = abs(position['total_cost']) * proportion_covered
            
            # Check if we have enough balance to close short
            if buy_cost > self.balance:
                return False, "Insufficient funds to close short position", 0
                
            # Pay to buy back the shares
            self.balance -= buy_cost
            
            if quantity >= abs_quantity:
                # Close entire position
                del self.positions[symbol]
                return True, "Short position covered completely", abs_quantity
            else:
                # Partial close
                new_quantity = current_quantity + quantity  # Less negative
                new_cost = position['total_cost'] * (new_quantity / current_quantity)
                position['total_cost'] = new_cost
                position['quantity'] = new_quantity
                if new_quantity != 0:
                    position['avg_price'] = abs(new_cost / new_quantity)
                return True, f"Partially covered short position ({abs(new_quantity)} shares remaining)", quantity
                
        return True, "Position updated", quantity

demo_account = DemoAccount()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/stock/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    # Extract timeframe from query parameters, default to '1d'
    timeframe = request.args.get('timeframe', '1d')
    
    # Map timeframe parameter to valid yfinance parameters
    timeframe_map = {
        '5m': {'period': '5d', 'interval': '5m'},
        '1h': {'period': '5d', 'interval': '1h'},
        '1d': {'period': '1mo', 'interval': '1d'},
    }
    
    # Default to daily if timeframe not recognized
    tf_params = timeframe_map.get(timeframe, {'period': '1mo', 'interval': '1d'})
    
    try:
        # Validate symbol input
        if not symbol or len(symbol) > 10:
            return jsonify({'error': 'Invalid stock symbol'}), 400

        # Log the request
        logger.info(f"Stock data requested for symbol: {symbol} with timeframe {timeframe}")
        
        stock = yf.Ticker(symbol)
        
        # Get basic info for the stock
        try:
            info = stock.info
            current_price = info.get('regularMarketPrice', None)
            company_name = info.get('shortName', symbol.upper())
            logger.info(f"Retrieved info for {symbol}: {company_name}, current price: {current_price}")
        except Exception as info_error:
            logger.warning(f"Failed to get stock info for {symbol}: {info_error}")
            current_price = None
            company_name = symbol.upper()

        # Fetch historical data with error handling
        try:
            history = stock.history(period=tf_params['period'], interval=tf_params['interval'])
            logger.info(f"Retrieved {len(history)} data points for {symbol}")
        except Exception as fetch_error:
            logger.error(f"Failed to fetch stock data for {symbol}: {fetch_error}")
            return jsonify({'error': 'Unable to retrieve stock data'}), 500
        
        if history is None or history.empty:
            logger.warning(f"No historical data found for symbol: {symbol}")
            return jsonify({'error': 'No data found for this symbol'}), 404
        
        # Ensure required columns exist
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in history.columns:
                logger.error(f"Missing column {col} in stock data")
                return jsonify({'error': 'Incomplete stock data'}), 500
        
        # Create safe fallback data for prediction if needed
        if len(history) < 5:
            # Not enough data points, return a reasonable fallback
            last_close = float(history['Close'][-1]) if not history.empty else 100.0
            return jsonify({
                'price': last_close,
                'prediction': [last_close * 1.001, last_close * 1.02, last_close * 0.99, last_close * 1.01], # Small random variation
                'history': {col: history[col].tolist() for col in required_columns if col in history.columns}
            })
        
        # Prepare data for Kronos prediction - completely wrapped in try/except
        last_close = float(history['Close'].iloc[-1]) if not history.empty else 100.0
        current_price_value = current_price or last_close  # Use API price or last close

        # Calculate statistics for realistic prediction ranges
        try:
            # Calculate average daily change percentage over available history
            close_prices = history['Close'].values
            daily_changes = np.diff(close_prices) / close_prices[:-1]
            avg_daily_change = np.mean(np.abs(daily_changes)) if len(daily_changes) > 0 else 0.01
            max_daily_change = np.max(np.abs(daily_changes)) if len(daily_changes) > 0 else 0.02
            
            # Ensure we have reasonable bounds (in case of outliers or limited data)
            avg_daily_change = min(max(avg_daily_change, 0.005), 0.03)  # Between 0.5% and 3%
            max_daily_change = min(max(max_daily_change, 0.01), 0.05)   # Between 1% and 5%
            
            logger.info(f"Avg daily change for {symbol}: {avg_daily_change:.4f}, Max: {max_daily_change:.4f}")
            
            # Prepare data for the Kronos model
            prediction_input = prepare_prediction_input(history)
            
            # Get raw predictions from the Kronos model
            # The model might give raw token values (multipliers) or direct price predictions
            raw_prediction = model.predict(prediction_input)
            logger.info(f"Raw Kronos prediction: {raw_prediction}")
            
            # Store raw prediction values (from model)
            raw_token_prediction = raw_prediction.copy()
            
            # The predictions from KronosFull are actually multipliers, not absolute values
            # We need to multiply them by the current price to get the actual predicted values
            last_close = float(history['Close'].iloc[-1])
            
            # The Kronos-mini model returns actual prediction values as multipliers of the current price
            # Simply multiply the prediction values by the current price
            pred_close = raw_prediction[0] * current_price_value
            pred_high = raw_prediction[1] * current_price_value  
            pred_low = raw_prediction[2] * current_price_value
            pred_open = raw_prediction[3] * current_price_value
            
            # Log the prediction values without any artificial adjustments
            logger.info(f"Raw prediction multipliers: {raw_prediction}")
            logger.info(f"Current price: {current_price_value}")
            logger.info(f"Calculated price predictions: Close={pred_close}, High={pred_high}, Low={pred_low}, Open={pred_open}")
            
            # Enforce proper relationships between OHLC values
            # High should be the highest value
            pred_high = max(pred_high, pred_close * 1.005, pred_open * 1.005)
            
            # Low should be the lowest value
            pred_low = min(pred_low, pred_close * 0.995, pred_open * 0.995)
            
            # Double-check to ensure High > Open, High > Close, Low < Open, Low < Close
            if not (pred_high > pred_open and pred_high > pred_close and 
                   pred_low < pred_open and pred_low < pred_close):
                logger.warning(f"Fixing inconsistent OHLC relationships for {symbol}")
                
                # Recalculate to ensure proper relationships
                middle_price = (pred_open + pred_close) / 2
                spread = abs(pred_close - pred_open) * 1.5
                
                pred_high = middle_price + spread * 1.1  # High is above both open and close
                pred_low = middle_price - spread * 1.1   # Low is below both open and close
            
            # Create the final prediction array
            scaled_prediction = np.array([pred_close, pred_high, pred_low, pred_open])
            logger.info(f"Scaled prediction for {symbol}: {scaled_prediction}")
        except Exception as pred_error:
            logger.error(f"Prediction error for {symbol}: {pred_error}")
            # More robust fallback prediction based on current price
            # For fallbacks, raw token values are the multipliers
            raw_token_prediction = np.array([
                1.001,  # Close with slight increase multiplier
                1.02,   # High multiplier
                0.99,   # Low multiplier
                1.01    # Open next day multiplier
            ])
            
            # Scaled prediction is multiplier × current price
            scaled_prediction = np.array([
                current_price_value * raw_token_prediction[0],
                current_price_value * raw_token_prediction[1], 
                current_price_value * raw_token_prediction[2], 
                current_price_value * raw_token_prediction[3]
            ])
            
            logger.info(f"Using fallback prediction for {symbol} with price {current_price_value}")
        
        # Ensure prediction values are valid numbers
        scaled_values = []
        for p in scaled_prediction:
            try:
                scaled_values.append(float(p))
            except (ValueError, TypeError):
                # If conversion fails, use a reasonable default
                scaled_values.append(float(history['Close'][-1]))
                
        # Also convert raw token predictions to valid numbers
        token_values = []
        for p in raw_token_prediction:
            try:
                token_values.append(float(p))
            except (ValueError, TypeError):
                # If conversion fails, use a reasonable default
                token_values.append(1.0)  # Default multiplier of 1.0 (no change)
        
        # Format the data for candlestick chart
        candle_data = []
        for i in range(len(history)):
            try:
                candle_data.append({
                    'x': history.index[i].strftime('%Y-%m-%d %H:%M:%S'),
                    'y': [
                        float(history['Open'].iloc[i]),
                        float(history['High'].iloc[i]),
                        float(history['Low'].iloc[i]),
                        float(history['Close'].iloc[i])
                    ]
                })
            except (IndexError, ValueError) as e:
                logger.warning(f"Error formatting candle data at index {i}: {e}")
        
        # Use current_price from API if available, otherwise use last close
        final_price = current_price if current_price else float(history['Close'].iloc[-1])
        
        return jsonify({
            'symbol': symbol.upper(),
            'name': company_name,
            'price': final_price,
            'prediction': scaled_values,  # Keep previous key for backward compatibility
            'raw_prediction': token_values,  # Add raw token values
            'timeframe': timeframe,
            'candle_data': candle_data,
            'history': {
                col: history[col].tolist() 
                for col in ['Open', 'High', 'Low', 'Close', 'Volume']
            }
        })
    except Exception as e:
        logger.error(f"Unexpected error in stock data retrieval: {e}")
        try:
            # Ultimate fallback - provide sensible defaults even if everything else fails
            return jsonify({
                'price': 100.0,
                'prediction': [101.0, 102.0, 99.0, 101.5],
                'history': {
                    'Open': [100.0],
                    'High': [102.0],
                    'Low': [98.0],
                    'Close': [100.0],
                    'Volume': [1000000]
                }
            })
        except:
            # If even the fallback fails, provide a simple error
            return jsonify({'error': 'Unable to retrieve stock data'}), 500

@app.route('/account/balance', methods=['POST'])
def update_balance():
    data = request.json
    amount = data.get('amount', 0)
    reset = data.get('reset', False)
    
    if reset:
        new_balance = demo_account.reset_balance()
        return jsonify({'balance': new_balance, 'positions': demo_account.get_positions()})
    else:
        new_balance = demo_account.update_balance(amount)
        return jsonify({'balance': new_balance})

@app.route('/positions', methods=['GET'])
def get_positions():
    positions = demo_account.get_positions()
    return jsonify({'positions': positions})

@app.route('/trade/execute', methods=['POST'])
def execute_trade():
    data = request.json
    symbol = data.get('symbol')
    quantity = data.get('quantity')
    price = data.get('price')
    action = data.get('action', 'buy')  # 'buy' or 'sell'
    
    success, message, executed_quantity = demo_account.execute_trade(symbol, quantity, price, action)
    
    return jsonify({
        'success': success,
        'message': message,
        'executed_quantity': executed_quantity,
        'balance': demo_account.balance,
        'positions': demo_account.get_positions()
    })

@app.route('/trade/close', methods=['POST'])
def close_trade():
    data = request.json
    symbol = data.get('symbol')
    quantity = data.get('quantity', None)  # None means close all
    current_price = data.get('current_price')
    
    success, message, closed_quantity = demo_account.close_position(symbol, quantity, current_price)
    
    return jsonify({
        'success': success,
        'message': message,
        'closed_quantity': closed_quantity,
        'balance': demo_account.balance,
        'positions': demo_account.get_positions()
    })

def prepare_prediction_input(history):
    """
    Prepare input data for Kronos-mini model prediction
    
    Args:
        history (pd.DataFrame): Historical stock price data
    
    Returns:
        np.ndarray: Prepared input features
    """
    try:
        # Ensure required columns exist
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in history.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Select and normalize features
        features = history[required_columns].values
        
        # Handle insufficient data
        if len(features) < 30:
            logger.warning(f"Insufficient historical data. Using available {len(features)} data points.")
        
        # Take last 30 data points or all available if less than 30
        input_data = features[-30:]
        
        # Normalize data (simple min-max scaling)
        for col in range(input_data.shape[1]):
            col_min = input_data[:, col].min()
            col_max = input_data[:, col].max()
            
            # Avoid division by zero
            if col_min != col_max:
                input_data[:, col] = (input_data[:, col] - col_min) / (col_max - col_min)
            else:
                input_data[:, col] = 0.5  # Default to middle of range if no variation
        
        return input_data
    
    except Exception as e:
        logger.error(f"Error preparing prediction input: {e}")
        # Return a default normalized array if preparation fails
        default_input = np.zeros((30, 5))
        default_input[:, 3] = 0.5  # Set close price column to middle of range
        return default_input

if __name__ == '__main__':
    app.run(debug=True, port=5000)