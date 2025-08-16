"""Main orchestration module for the AI trading workflow."""

from __future__ import annotations

import asyncio
import pandas as pd

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import settings
from core.database import Database
from data.market_data import fetch_top_tickers, fetch_price_data, fetch_news_sentiment, fetch_chart_snapshot
from analysis.vision import describe_chart
from strategy.signals import generate_signal
from strategy.risk import position_size, should_trade
from execution.trading import get_account, place_order
from reporting.reports import generate_report, send_email


db = Database(settings.postgres_dsn)


async def daily_workflow() -> None:
    tickers = await fetch_top_tickers()
    signals = []
    trades = []
    account = get_account()
    balance = float(account.cash)
    loss_ledger = {}

    for symbol in tickers:
        if not should_trade(symbol, loss_ledger):
            continue
        price_data = await fetch_price_data(symbol)
        price_df = None
        if "values" in price_data:
            price_df = pd.DataFrame(price_data["values"]).iloc[::-1]
        else:
            ts = price_data.get("Time Series (Daily)", {})
            price_df = pd.DataFrame([
                {"date": k, **v} for k, v in ts.items()
            ]).sort_values("date")
        sentiment_data = await fetch_news_sentiment(symbol)
        sentiment_score = sentiment_data.get("overall_sentiment_score", 0)
        ai_score = 0.0  # placeholder for Danelfin score which isn't returned in top-tickers endpoint

        # Optional chart analysis via LLM vision
        try:
            chart_img = await fetch_chart_snapshot(symbol)
            _ = await describe_chart(chart_img, "https://example.com/vision", "demo")
        except Exception:
            pass

        signal = generate_signal(symbol, price_df, ai_score, sentiment_score)
        signals.append(signal)

        if signal.direction in {"buy", "sell"}:
            stop_loss_distance = 1  # placeholder
            qty = position_size(balance, 0.01, stop_loss_distance)
            place_order(symbol, int(qty), signal.direction)
            trades.append(f"{signal.direction} {qty} {symbol}")

    report = generate_report(signals, trades, 0.0)
    send_email("Daily Market Report", report, [settings.smtp_user])


async def main() -> None:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(daily_workflow, "cron", hour=0, minute=0)
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    asyncio.run(main())
