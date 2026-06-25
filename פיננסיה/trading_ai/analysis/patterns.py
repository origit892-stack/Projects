from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from trading_ai.models import Direction


@dataclass(frozen=True)
class PatternMatch:
    name: str
    direction: Direction
    breakout_price: float
    measured_move: float
    last_swing: float
    index: pd.Timestamp


def detect_latest_pattern(df: pd.DataFrame) -> PatternMatch | None:
    if len(df) < 60:
        return None

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    breakout = _support_resistance_breakout(df)
    if breakout:
        return breakout

    flag = _flag_breakout(df)
    if flag:
        return flag

    head_shoulders = _head_shoulders_breakout(df)
    if head_shoulders:
        return head_shoulders

    if previous["close"] >= previous["bb_lower"] and latest["close"] < latest["bb_lower"]:
        move = float(df["atr_14"].iloc[-1] * 3)
        return PatternMatch("Bollinger Support Breakdown", Direction.SHORT, float(latest["close"]), move, float(df["high"].tail(10).max()), df.index[-1])

    if previous["close"] <= previous["bb_upper"] and latest["close"] > latest["bb_upper"]:
        move = float(df["atr_14"].iloc[-1] * 3)
        return PatternMatch("Bollinger Resistance Breakout", Direction.LONG, float(latest["close"]), move, float(df["low"].tail(10).min()), df.index[-1])

    return None


def _support_resistance_breakout(df: pd.DataFrame) -> PatternMatch | None:
    lookback = df.iloc[-31:-1]
    latest = df.iloc[-1]
    resistance = float(lookback["high"].max())
    support = float(lookback["low"].min())
    atr_value = float(latest["atr_14"])

    if latest["close"] > resistance and latest["volume"] > lookback["volume"].mean():
        return PatternMatch("Resistance Breakout", Direction.LONG, float(latest["close"]), atr_value * 3, float(lookback["low"].tail(10).min()), df.index[-1])

    if latest["close"] < support and latest["volume"] > lookback["volume"].mean():
        return PatternMatch("Support Breakdown", Direction.SHORT, float(latest["close"]), atr_value * 3, float(lookback["high"].tail(10).max()), df.index[-1])

    return None


def _flag_breakout(df: pd.DataFrame) -> PatternMatch | None:
    pole = df.iloc[-45:-20]
    flag = df.iloc[-20:]
    pole_move = float(pole["close"].iloc[-1] - pole["close"].iloc[0])
    if abs(pole_move) < float(df["atr_14"].iloc[-1] * 4):
        return None

    x = np.arange(len(flag))
    highs_slope = float(np.polyfit(x, flag["high"], 1)[0])
    lows_slope = float(np.polyfit(x, flag["low"], 1)[0])
    latest_close = float(flag["close"].iloc[-1])

    if pole_move < 0 and highs_slope > 0 and lows_slope > 0 and latest_close < float(flag["low"].iloc[:-1].min()):
        return PatternMatch("Bearish Flag", Direction.SHORT, latest_close, abs(pole_move), float(flag["high"].max()), df.index[-1])

    if pole_move > 0 and highs_slope < 0 and lows_slope < 0 and latest_close > float(flag["high"].iloc[:-1].max()):
        return PatternMatch("Bullish Flag", Direction.LONG, latest_close, abs(pole_move), float(flag["low"].min()), df.index[-1])

    return None


def _head_shoulders_breakout(df: pd.DataFrame) -> PatternMatch | None:
    window = df.iloc[-80:]
    highs = _local_extrema(window["high"], "max")
    lows = _local_extrema(window["low"], "min")
    if len(highs) < 3 or len(lows) < 2:
        return None

    left, head, right = highs[-3:]
    if not (head[1] > left[1] and head[1] > right[1]):
        return None
    shoulder_tolerance = abs(left[1] - right[1]) / max(left[1], right[1])
    if shoulder_tolerance > 0.04:
        return None

    neckline = float(np.mean([low[1] for low in lows[-2:]]))
    latest_close = float(window["close"].iloc[-1])
    if latest_close < neckline:
        measured_move = float(head[1] - neckline)
        return PatternMatch("Head and Shoulders", Direction.SHORT, latest_close, measured_move, float(right[1]), df.index[-1])
    return None


def _local_extrema(series: pd.Series, kind: str) -> list[tuple[pd.Timestamp, float]]:
    values: list[tuple[pd.Timestamp, float]] = []
    for i in range(2, len(series) - 2):
        point = float(series.iloc[i])
        neighbours = series.iloc[i - 2 : i + 3]
        if kind == "max" and point == float(neighbours.max()):
            values.append((series.index[i], point))
        if kind == "min" and point == float(neighbours.min()):
            values.append((series.index[i], point))
    return values

