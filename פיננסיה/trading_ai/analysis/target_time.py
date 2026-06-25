from __future__ import annotations

import numpy as np
import pandas as pd


def target_eta_label(df: pd.DataFrame, entry: float, target: float, timeframe: str) -> str:
    distance = abs(target - entry)
    recent_move = df["close"].diff().abs().tail(30).replace(0, np.nan).mean()
    atr_value = float(df["atr_14"].iloc[-1]) if "atr_14" in df else 0.0
    movement_per_candle = max(float(recent_move) if pd.notna(recent_move) else 0.0, atr_value * 0.35, entry * 0.001)
    bars = max(1, int(np.ceil(distance / movement_per_candle)))
    return f"בערך {bars} נרות / {_format_duration(bars * _timeframe_minutes(timeframe))}"


def _timeframe_minutes(timeframe: str) -> int:
    unit = timeframe[-1]
    amount_text = timeframe[:-1]
    if not amount_text.isdigit():
        return 60
    amount = int(amount_text)
    if unit == "m":
        return amount
    if unit == "h":
        return amount * 60
    if unit == "d":
        return amount * 24 * 60
    if unit == "w":
        return amount * 7 * 24 * 60
    return 60


def _format_duration(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes} דקות"
    hours = minutes / 60
    if hours < 24:
        return f"{hours:.1f} שעות"
    days = hours / 24
    if days < 14:
        return f"{days:.1f} ימים"
    weeks = days / 7
    return f"{weeks:.1f} שבועות"
