"""Trade execution via Alpaca Paper API."""

from __future__ import annotations

import alpaca_trade_api as tradeapi

from core.config import settings


def get_client() -> tradeapi.REST:
    return tradeapi.REST(key_id=settings.alpaca_api_key, secret_key=settings.alpaca_api_secret, base_url="https://paper-api.alpaca.markets")


def get_account() -> tradeapi.entity.Account:
    client = get_client()
    return client.get_account()


def place_order(symbol: str, qty: int, side: str, take_profit: float | None = None, stop_loss: float | None = None) -> None:
    """Place a market or bracket order depending on provided limits."""
    client = get_client()
    order_params = {"symbol": symbol, "qty": qty, "side": side, "type": "market", "time_in_force": "gtc"}
    if take_profit or stop_loss:
        order_params["type"] = "bracket"
        order_params["take_profit"] = {"limit_price": take_profit} if take_profit else None
        order_params["stop_loss"] = {"stop_price": stop_loss} if stop_loss else None
    client.submit_order(**order_params)
