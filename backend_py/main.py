from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
import os
from dotenv import load_dotenv
import httpx
from pydantic import BaseModel
from database import get_db, User, Signal, Trade, engine, Base
from signal_engine import generate_signal
from typing import List
import uuid
from fastapi_users import FastAPIUsers
from auth import get_user_manager
from fastapi_users.authentication import JWTStrategy, BearerTransport, AuthenticationBackend
import asyncio
from typing import List
from fastapi_users import schemas
from pydantic import EmailStr

class UserRead(schemas.BaseUser[int]):
    pass

class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str

class UserUpdate(schemas.BaseUserUpdate):
    pass

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

SECRET = os.getenv("SECRET_KEY", "your-secret-key-here")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

manager = ConnectionManager()

app = FastAPI(title="DeltaPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Auth setup
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=lambda: JWTStrategy(secret=SECRET, lifetime_seconds=3600),
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
import json

# ... existing code ...

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

@app.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial data
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]  # Default symbols
        while True:
            prices = {}
            for symbol in symbols:
                try:
                    price_data = await get_price_async(symbol)
                    prices[symbol] = price_data["price"]
                except Exception as e:
                    print(f"Error getting price for {symbol}: {e}")
                    prices[symbol] = None
            await websocket.send_text(json.dumps({"type": "prices", "data": prices}))
            await asyncio.sleep(5)  # Update every 5 seconds
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)

class PriceResponse(BaseModel):
    symbol: str
    price: float

class SignalRequest(BaseModel):
    symbol: str
    prices: list[float]

class CreateSignal(BaseModel):
    symbol: str
    price: float
    confidence: float = 0.5

class OrderRequest(BaseModel):
    symbol: str
    side: str  # "buy" or "sell"
    qty: float
    order_type: str = "market"
    time_in_force: str = "gtc"

@app.get("/")
@app.get("/debug/env")
def debug_env():
    return {
        "ALPACA_API_KEY": os.getenv("ALPACA_API_KEY"),
        "ALPACA_SECRET_KEY": os.getenv("ALPACA_SECRET_KEY"),
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "SECRET_KEY": os.getenv("SECRET_KEY")
    }

async def get_price_async(symbol: str):
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    
    if not api_key or not secret_key:
        return {"symbol": symbol, "price": None}
    
    async with httpx.AsyncClient() as client:
        headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key
        }
        response = await client.get(
            f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest",
            headers=headers
        )
    
    if response.status_code != 200:
        return {"symbol": symbol, "price": None}
    
    data = response.json()
    price = data["quote"]["ap"]
    
    return {"symbol": symbol, "price": price}


@app.get("/api/market/price/{symbol}")
def get_market_price(symbol: str):
    return get_price(symbol)


def get_price(symbol: str) -> PriceResponse:
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    
    if not api_key or not secret_key:
        return PriceResponse(symbol=symbol, price=None)
    
    with httpx.Client() as client:
        headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key
        }
        response = client.get(
            f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest",
            headers=headers
        )
    
    if response.status_code != 200:
        return PriceResponse(symbol=symbol, price=None)
    
    data = response.json()
    price = data["quote"]["ap"]
    
    return PriceResponse(symbol=symbol, price=price)

@app.post("/api/signals/generate")
def get_signal(request: SignalRequest):
    signal = generate_signal(request.prices)
    return {"signal": signal, "prices": request.prices}

# DB CRUD: Signals
@app.post("/api/signals/")
def create_signal(signal: CreateSignal, current_user: User = Depends(fastapi_users.current_user()), db: Session = Depends(get_db)):
    db_signal = Signal(
        user_id=current_user.id,
        symbol=signal.symbol,
        signal=generate_signal([signal.price] * 20),  # Temp
        price=signal.price,
        confidence=signal.confidence
    )
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    return db_signal

@app.get("/api/signals/")
def list_signals(current_user: User = Depends(fastapi_users.current_user()), db: Session = Depends(get_db)):
    return db.query(Signal).filter(Signal.user_id == current_user.id).all()

@app.get("/api/trading/account")
def get_account():
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    if not api_key or not secret_key:
        raise HTTPException(status_code=500, detail="Alpaca credentials not set")
    
    with httpx.Client() as client:
        headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key
        }
        response = client.get("https://paper-api.alpaca.markets/v2/account", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch account")
        return response.json()

@app.get("/api/trading/positions")
def get_positions():
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    if not api_key or not secret_key:
        raise HTTPException(status_code=500, detail="Alpaca credentials not set")
    
    with httpx.Client() as client:
        headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key
        }
        response = client.get("https://paper-api.alpaca.markets/v2/positions", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch positions")
        return response.json()

@app.post("/api/trading/order")
def submit_order(request: OrderRequest, current_user: User = Depends(fastapi_users.current_user()), db: Session = Depends(get_db)):
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    if not api_key or not secret_key:
        raise HTTPException(status_code=500, detail="Alpaca credentials not set")
    
    # Fetch current price
    price_resp = get_price(request.symbol)
    current_price = price_resp.price
    
    # Map side
    alpaca_side = request.side.lower()
    if alpaca_side not in ["buy", "sell"]:
        raise HTTPException(status_code=400, detail="Side must be 'buy' or 'sell'")
    
    db_side = "LONG" if alpaca_side == "buy" else "SHORT"
    
    # Submit order to Alpaca
    with httpx.Client() as client:
        headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key
        }
        order_data = {
            "symbol": request.symbol,
            "qty": str(request.qty),
            "side": alpaca_side,
            "type": request.order_type,
            "time_in_force": request.time_in_force
        }
        response = client.post("https://paper-api.alpaca.markets/v2/orders", headers=headers, json=order_data)
    
    if response.status_code not in [200, 201]:
        raise HTTPException(status_code=response.status_code, detail="Order submission failed: " + response.text)
    
    order_result = response.json()
    
    # Save to DB
    db_trade = Trade(
        user_id=current_user.id,
        symbol=request.symbol,
        side=db_side,
        entry_price=current_price,
        size=request.qty,
        status="OPEN"
    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    
    return {"order": order_result, "trade": db_trade}

@app.get("/api/market/bars/{symbol}")
def get_bars(
    symbol: str,
    timeframe: str = "1Min",
    limit: int = 50
):
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    
    if not api_key or not secret_key:
        # Mock data fallback
        import random
        import time
        bars = []
        base_price = 175.0
        for i in range(limit):
            bars.append({
                "timestamp": int(time.time() * 1000) - (limit - i) * 60000,
                "open": base_price + random.uniform(-0.5, 0.5),
                "high": base_price + random.uniform(0, 1),
                "low": base_price + random.uniform(-1, 0),
                "close": base_price + random.uniform(-0.5, 0.5) + (i * 0.01 if i % 5 == 0 else 0),
                "volume": random.randint(100000, 1000000)
            })
        return {"bars": bars}
    
    with httpx.Client() as client:
        headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key
        }
        params = {
            "timeframe": timeframe,
            "limit": str(limit),
            "adjustment": "all",
            "feed": "iex"  # or sip for more accurate
        }
        response = client.get(
            f"https://data.alpaca.markets/v2/stocks/{symbol}/bars",
            headers=headers,
            params=params
        )
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch bars")
    
    data = response.json()
    return data


@app.get("/api/market/quotes")
def get_quotes(symbols: str):
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    if not api_key or not secret_key:
        raise HTTPException(status_code=500, detail="Alpaca credentials not set")
    
    symbol_list = symbols.split(',')
    quotes = []
    
    with httpx.Client() as client:
        headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key
        }
        
        for symbol in symbol_list:
            symbol = symbol.strip()
            try:
                response = client.get(
                    f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest",
                    headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    quotes.append({
                        "symbol": symbol,
                        "price": data["quote"]["ap"]
                    })
            except:
                # Skip failed symbols
                continue
    
    return {"quotes": quotes}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

