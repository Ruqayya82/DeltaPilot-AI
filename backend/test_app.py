import pytest
import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app, demo_account

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_stock_data_retrieval(client):
    """Test stock data retrieval endpoint"""
    response = client.get('/stock/AAPL')
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'price' in data
    assert 'prediction' in data
    assert len(data['prediction']) == 4

def test_account_balance_update(client):
    """Test account balance update"""
    initial_balance = demo_account.balance
    
    response = client.post('/account/balance', json={'amount': 1000})
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'balance' in data
    assert data['balance'] == initial_balance + 1000

def test_trade_open(client):
    """Test opening a trading position"""
    initial_balance = demo_account.balance
    trade_data = {
        'symbol': 'AAPL',
        'quantity': 10,
        'price': 150.00
    }
    
    response = client.post('/trade/open', json=trade_data)
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    assert data['balance'] == initial_balance - (trade_data['quantity'] * trade_data['price'])

def test_trade_close(client):
    """Test closing a trading position"""
    # First, open a position
    trade_open_data = {
        'symbol': 'AAPL',
        'quantity': 10,
        'price': 150.00
    }
    client.post('/trade/open', json=trade_open_data)
    
    # Then close the position
    trade_close_data = {
        'symbol': 'AAPL',
        'quantity': 5,
        'current_price': 155.00
    }
    
    response = client.post('/trade/close', json=trade_close_data)
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True