"""Risk management utilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Position:
    symbol: str
    size: float
    stop_loss: float
    take_profit: float


def position_size(account_balance: float, risk_perc: float, stop_loss_distance: float) -> float:
    """Calculate position size based on account balance and risk percentage."""
    risk_amount = account_balance * risk_perc
    return risk_amount / stop_loss_distance if stop_loss_distance else 0


def should_trade(symbol: str, loss_ledger: dict[str, float], cooldown_days: int = 5) -> bool:
    """No-repeat-loss policy: avoid symbols that lost recently."""
    from datetime import datetime, timedelta

    last_loss = loss_ledger.get(symbol)
    if not last_loss:
        return True
    return datetime.utcnow() - last_loss > timedelta(days=cooldown_days)
