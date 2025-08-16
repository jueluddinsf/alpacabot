# AI Trading Workflow Scaffold

This repository provides a modular scaffold for an AI-powered trading workflow. It integrates market data, technical analysis, news sentiment, and rule-based strategies with risk management and execution via the Alpaca Paper API.

## Features

- **Market Data**: Top tickers from Danelfin, price data from TwelveData (AlphaVantage fallback), news sentiment, and optional chart snapshots.
- **Analysis**: Technical indicators (RSI, MACD, EMA, Bollinger Bands, Fibonacci), trend detection, and an LLM vision module for chart interpretation.
- **Strategy & Risk**: Signal generation blending AI scores, sentiment, and technicals. Includes position sizing, stop-loss/take-profit, and no-repeat-loss policy.
- **Execution**: Trade placement on Alpaca Paper API with balance checks.
- **Storage**: PostgreSQL with `pgvector` for tickers, signals, trades, loss ledger, and reports.
- **Reporting**: Markdown reports emailed via SMTP.
- **Scheduler**: Uses APScheduler for daily task orchestration.

## Project Structure

```
core/        # Configuration and database helpers
data/        # Market data retrieval
analysis/    # Technical analysis, trend detection, vision module
strategy/    # Signal generation and risk management
execution/   # Trade execution via Alpaca
reporting/   # Report generation and email
```

## Getting Started

1. **Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Environment**
   - Copy `.env.example` to `.env` and fill in API keys.
3. **Database**
   - Start PostgreSQL with pgvector:
     ```bash
     docker-compose up -d
     psql $POSTGRES_DSN -f schema.sql
     ```
4. **Run**
   ```bash
   python main.py
   ```

## License

MIT
