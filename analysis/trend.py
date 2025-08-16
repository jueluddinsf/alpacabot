"""Trend regime detection."""

from __future__ import annotations

import pandas as pd


def detect_trend(price_series: pd.Series, short: int = 50, long: int = 200) -> str:
    """Simple moving-average crossover regime detection."""
    ma_short = price_series.rolling(window=short).mean()
    ma_long = price_series.rolling(window=long).mean()
    if ma_short.iloc[-1] > ma_long.iloc[-1]:
        return "bull"
    if ma_short.iloc[-1] < ma_long.iloc[-1]:
        return "bear"
    return "neutral"
