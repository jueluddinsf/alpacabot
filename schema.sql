-- PostgreSQL schema for trading bot
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS tickers (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    trade_date DATE NOT NULL,
    ai_score REAL,
    sentiment REAL,
    technicals JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    signal_date TIMESTAMP DEFAULT NOW(),
    direction TEXT,
    confidence REAL,
    embedding VECTOR(1536)
);

CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    entry_time TIMESTAMP,
    exit_time TIMESTAMP,
    quantity REAL,
    entry_price REAL,
    exit_price REAL,
    pnl REAL
);

CREATE TABLE IF NOT EXISTS loss_ledger (
    symbol TEXT PRIMARY KEY,
    last_loss TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    report_date DATE DEFAULT CURRENT_DATE,
    content TEXT
);
