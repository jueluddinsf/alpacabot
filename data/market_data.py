"""Market data retrieval functions using async HTTP requests."""

from __future__ import annotations

import httpx

from core.config import settings


async def fetch_top_tickers(limit: int = 10) -> list[str]:
    """Get top-ranked tickers from the Danelfin API."""
    url = "https://api.danelfin.com/v1/tickers/top"
    params = {"limit": limit}
    headers = {"Authorization": f"Bearer {settings.danelfin_api_key}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    return [item["symbol"] for item in data.get("tickers", [])]


async def fetch_price_data(symbol: str) -> dict:
    """Fetch daily price data from TwelveData with AlphaVantage fallback."""
    td_url = "https://api.twelvedata.com/time_series"
    td_params = {
        "symbol": symbol,
        "interval": "1day",
        "outputsize": 500,
        "apikey": settings.twelvedata_api_key,
    }
    async with httpx.AsyncClient() as client:
        td_resp = await client.get(td_url, params=td_params)
        if td_resp.status_code == 200 and "values" in td_resp.json():
            return td_resp.json()
        av_url = "https://www.alphavantage.co/query"
        av_params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "apikey": settings.alphavantage_api_key,
        }
        av_resp = await client.get(av_url, params=av_params)
        av_resp.raise_for_status()
        return av_resp.json()


async def fetch_news_sentiment(symbol: str) -> dict:
    """Fetch real-time news sentiment scores from AlphaVantage."""
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": symbol,
        "apikey": settings.alphavantage_api_key,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


async def fetch_chart_snapshot(symbol: str) -> bytes:
    """Optionally retrieve a chart image via the Chart-img API."""
    url = "https://api.chart-img.com/v1/tradingview/advanced-chart"
    params = {"symbol": symbol, "interval": "D"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=60)
        resp.raise_for_status()
        return resp.content
