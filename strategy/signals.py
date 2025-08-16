"""Signal generation by blending AI scores, sentiment, and technicals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import pandas as pd

from analysis.technical import rsi, macd, ema, bollinger_bands
from analysis.trend import detect_trend


@dataclass
class Signal:
    symbol: str
    direction: str
    confidence: float
    technicals: Dict[str, Any]
    sentiment: float
    ai_score: float


def generate_signal(symbol: str, price_df: pd.DataFrame, ai_score: float, sentiment: float) -> Signal:
    """Generate trading signal by blending multiple inputs."""
    close = price_df["close"].astype(float)
    rsi_val = rsi(close).iloc[-1]
    macd_vals = macd(close).iloc[-1].to_dict()
    ema_val = ema(close).iloc[-1]
    bb_vals = bollinger_bands(close).iloc[-1].to_dict()
    trend = detect_trend(close)

    score = ai_score * 0.4 + sentiment * 0.2 + (100 - abs(rsi_val - 50)) / 100 * 0.2
    score += (1 if trend == "bull" else -1 if trend == "bear" else 0) * 0.2
    direction = "buy" if score > 0.6 else "sell" if score < 0.4 else "hold"

    technicals = {"rsi": rsi_val, "ema": ema_val, "macd": macd_vals, "bollinger": bb_vals, "trend": trend}
    return Signal(symbol=symbol, direction=direction, confidence=score, technicals=technicals, sentiment=sentiment, ai_score=ai_score)
