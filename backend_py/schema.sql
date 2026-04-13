-- DeltaPilot DB Schema (Run in Supabase SQL Editor)
-- https://supabase.com/docs/guides/database/overview

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Signals table
CREATE TABLE signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    signal VARCHAR(10) NOT NULL,  -- BUY/SELL/HOLD
    price DOUBLE PRECISION,
    confidence DOUBLE PRECISION DEFAULT 0.5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trades table
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,  -- LONG/SHORT
    entry_price DOUBLE PRECISION NOT NULL,
    stop_loss DOUBLE PRECISION,
    take_profit DOUBLE PRECISION,
    size DOUBLE PRECISION,
    status VARCHAR(20) DEFAULT 'OPEN',  -- OPEN/CLOSED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP WITH TIME ZONE
);

-- Index for performance
CREATE INDEX idx_signals_symbol ON signals(symbol);
CREATE INDEX idx_signals_user ON signals(user_id);
CREATE INDEX idx_trades_user ON trades(user_id);
