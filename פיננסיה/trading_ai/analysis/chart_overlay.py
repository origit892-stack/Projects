from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from trading_ai.analysis.engine import AnalysisEngine
from trading_ai.analysis.indicators import add_indicators
from trading_ai.analysis.target_time import target_eta_label
from trading_ai.models import Direction, TradeSignal


@dataclass(frozen=True)
class OverlayLine:
    label: str
    kind: str
    color: str
    y0: float
    y1: float | None = None
    x0: pd.Timestamp | None = None
    x1: pd.Timestamp | None = None
    dash: str = "dash"


@dataclass(frozen=True)
class ChartAnalysis:
    action: str
    confidence: str
    reason: str
    signal: TradeSignal | None = None
    lines: list[OverlayLine] = field(default_factory=list)
    target_eta_label: str | None = None
    volume_ratio: float | None = None


def analyze_chart(symbol: str, timeframe: str, candles: pd.DataFrame, min_risk_reward: float = 2.0) -> ChartAnalysis:
    prepared = add_indicators(candles).dropna()
    if len(prepared) < 60:
        return ChartAnalysis("WAIT", "LOW", "אין מספיק נרות לניתוח יציב.")

    signal = AnalysisEngine(min_risk_reward).analyze(symbol, timeframe, candles)
    lines = _base_levels(prepared)
    lines.extend(_trend_channel(prepared))
    lines.extend(_fibonacci_levels(prepared))

    if signal:
        target_eta = signal.target_eta_label or target_eta_label(prepared, signal.entry, signal.target, timeframe)
        lines.extend(_signal_lines(signal, target_eta))
        action = "BUY" if signal.direction == Direction.LONG else "SELL"
        hebrew_action = "כניסה לקנייה" if action == "BUY" else "מכירה / שורט"
        return _apply_volume_confirmation(
            prepared,
            ChartAnalysis(
            action=action,
            confidence="HIGH",
            reason=f"{hebrew_action}: זוהתה תבנית {signal.pattern} עם יחס סיכוי/סיכון {signal.risk_reward:.2f}. יעד משוער: {target_eta}.",
            signal=signal,
            lines=lines,
            target_eta_label=target_eta,
            ),
        )

    pending = _pending_pattern(prepared, timeframe)
    if pending:
        return ChartAnalysis(
            action=pending.action,
            confidence=pending.confidence,
            reason=pending.reason,
            signal=pending.signal,
            lines=lines + pending.lines,
            target_eta_label=pending.target_eta_label,
            volume_ratio=pending.volume_ratio,
        )

    return _market_context(prepared, lines)


def _base_levels(df: pd.DataFrame) -> list[OverlayLine]:
    lookback = df.tail(40)
    support = float(lookback["low"].min())
    resistance = float(lookback["high"].max())
    return [
        OverlayLine("Resistance", "horizontal", "#f97316", resistance),
        OverlayLine("Support", "horizontal", "#22c55e", support),
    ]


def _signal_lines(signal: TradeSignal, target_eta_label: str | None = None) -> list[OverlayLine]:
    target_label = "Target"
    if target_eta_label:
        target_label = f"Target ({target_eta_label})"
    return [
        OverlayLine("Entry", "horizontal", "#38bdf8", signal.entry, dash="solid"),
        OverlayLine(target_label, "horizontal", "#22c55e", signal.target, dash="solid"),
        OverlayLine("Stop Loss", "horizontal", "#ef4444", signal.stop_loss, dash="solid"),
    ]


def _trend_channel(df: pd.DataFrame) -> list[OverlayLine]:
    window = df.tail(24)
    if len(window) < 10:
        return []

    x = np.arange(len(window))
    high_slope, high_intercept = np.polyfit(x, window["high"], 1)
    low_slope, low_intercept = np.polyfit(x, window["low"], 1)
    x0 = window.index[0]
    x1 = window.index[-1]
    return [
        OverlayLine("Trend Resistance", "segment", "#a855f7", float(high_intercept), float(high_slope * (len(window) - 1) + high_intercept), x0, x1),
        OverlayLine("Trend Support", "segment", "#a855f7", float(low_intercept), float(low_slope * (len(window) - 1) + low_intercept), x0, x1),
    ]


def _fibonacci_levels(df: pd.DataFrame) -> list[OverlayLine]:
    window = df.tail(80)
    swing_high = float(window["high"].max())
    swing_low = float(window["low"].min())
    if swing_high <= swing_low:
        return []

    high_index = window["high"].idxmax()
    low_index = window["low"].idxmin()
    upward_swing = low_index < high_index
    distance = swing_high - swing_low
    color = "#64748b"

    if upward_swing:
        return [
            OverlayLine(f"Fib {level:.1%}", "horizontal", color, swing_high - distance * level, dash="dot")
            for level in [0.382, 0.5, 0.618]
        ]

    return [
        OverlayLine(f"Fib {level:.1%}", "horizontal", color, swing_low + distance * level, dash="dot")
        for level in [0.382, 0.5, 0.618]
    ]


def _pending_pattern(df: pd.DataFrame, timeframe: str) -> ChartAnalysis | None:
    flag = _flag_setup(df, timeframe)
    if flag:
        return flag

    triangle = _triangle_setup(df, timeframe)
    if triangle:
        return triangle

    wedge = _wedge_setup(df, timeframe)
    if wedge:
        return wedge

    double = _double_top_bottom(df, timeframe)
    if double:
        return double

    rectangle = _rectangle_setup(df, timeframe)
    if rectangle:
        return rectangle

    return None


def _double_top_bottom(df: pd.DataFrame, timeframe: str) -> ChartAnalysis | None:
    window = df.tail(90)
    highs = _local_extrema(window["high"], "max")
    lows = _local_extrema(window["low"], "min")
    atr_value = float(df["atr_14"].iloc[-1])
    if len(highs) >= 2 and len(lows) >= 1:
        first, second = highs[-2:]
        first_pos = window.index.get_loc(first[0])
        second_pos = window.index.get_loc(second[0])
        separated = second_pos - first_pos >= 8
        recent_second_peak = len(window) - second_pos <= 35
        peaks_close = abs(first[1] - second[1]) / max(first[1], second[1]) < 0.01
        if separated and recent_second_peak and peaks_close:
            neckline = float(window.loc[first[0] : second[0], "low"].min())
            latest = float(window["close"].iloc[-1])
            top = float(max(first[1], second[1]))
            has_meaningful_trough = top - neckline >= atr_value * 2
            price_is_relevant = latest < top and (latest - neckline) <= (top - neckline) * 0.75
            if not (has_meaningful_trough and price_is_relevant):
                return None
            lines = [
                OverlayLine("Double Top Resistance", "horizontal", "#f97316", top),
                OverlayLine("Neckline", "horizontal", "#ef4444", neckline),
            ]
            if latest < neckline:
                return _manual_signal(df, timeframe, "SELL", "HIGH", "Double Top נשבר מטה.", latest, neckline, top, lines)
            return ChartAnalysis("WAIT", "MEDIUM", "Double Top אפשרי: מחכים לשבירת קו הצוואר.", lines=lines)

    if len(lows) >= 2 and len(highs) >= 1:
        first, second = lows[-2:]
        first_pos = window.index.get_loc(first[0])
        second_pos = window.index.get_loc(second[0])
        separated = second_pos - first_pos >= 8
        recent_second_trough = len(window) - second_pos <= 35
        troughs_close = abs(first[1] - second[1]) / max(first[1], second[1]) < 0.01
        if separated and recent_second_trough and troughs_close:
            neckline = float(window.loc[first[0] : second[0], "high"].max())
            latest = float(window["close"].iloc[-1])
            bottom = float(min(first[1], second[1]))
            has_meaningful_peak = neckline - bottom >= atr_value * 2
            price_is_relevant = latest > bottom and (neckline - latest) <= (neckline - bottom) * 0.75
            if not (has_meaningful_peak and price_is_relevant):
                return None
            lines = [
                OverlayLine("Double Bottom Support", "horizontal", "#22c55e", bottom),
                OverlayLine("Neckline", "horizontal", "#38bdf8", neckline),
            ]
            if latest > neckline:
                return _manual_signal(df, timeframe, "BUY", "HIGH", "Double Bottom נפרץ מעלה.", latest, neckline, bottom, lines)
            return ChartAnalysis("WAIT", "MEDIUM", "Double Bottom אפשרי: מחכים לפריצת קו הצוואר.", lines=lines)

    return None


def _triangle_setup(df: pd.DataFrame, timeframe: str) -> ChartAnalysis | None:
    window = df.tail(60)
    if len(window) < 40:
        return None

    high_slope, high_intercept = _fit_line(window["high"])
    low_slope, low_intercept = _fit_line(window["low"])
    start_gap = abs(float(high_intercept - low_intercept))
    end_resistance = float(high_slope * (len(window) - 1) + high_intercept)
    end_support = float(low_slope * (len(window) - 1) + low_intercept)
    end_gap = abs(end_resistance - end_support)
    if start_gap <= 0 or end_gap >= start_gap * 0.8:
        return None

    price = float(window["close"].iloc[-1])
    atr_value = float(df["atr_14"].iloc[-1])
    high_slope_pct = high_slope / max(price, 1e-9)
    low_slope_pct = low_slope / max(price, 1e-9)
    flat_tolerance = atr_value / max(price, 1e-9)
    x0 = window.index[0]
    x1 = window.index[-1]
    lines = [
        OverlayLine("Triangle Resistance", "segment", "#f97316", float(high_intercept), end_resistance, x0, x1),
        OverlayLine("Triangle Support", "segment", "#22c55e", float(low_intercept), end_support, x0, x1),
    ]

    pattern_name = None
    if high_slope < 0 and low_slope > 0:
        pattern_name = "Symmetrical Triangle"
    elif abs(high_slope_pct) < flat_tolerance * 0.15 and low_slope > 0:
        pattern_name = "Ascending Triangle"
    elif high_slope < 0 and abs(low_slope_pct) < flat_tolerance * 0.15:
        pattern_name = "Descending Triangle"

    if not pattern_name:
        return None

    height = max(start_gap, atr_value * 2)
    if price > end_resistance:
        target = price + height
        eta = target_eta_label(df, price, target, timeframe)
        return _apply_volume_confirmation(df, ChartAnalysis("BUY", "HIGH", f"{pattern_name} נפרץ מעלה. יעד משוער: {eta}.", lines=lines + _entry_target_stop(price, target, end_support, eta), target_eta_label=eta))
    if price < end_support:
        target = price - height
        eta = target_eta_label(df, price, target, timeframe)
        return _apply_volume_confirmation(df, ChartAnalysis("SELL", "HIGH", f"{pattern_name} נשבר מטה. יעד משוער: {eta}.", lines=lines + _entry_target_stop(price, target, end_resistance, eta), target_eta_label=eta))
    return ChartAnalysis("WAIT", "MEDIUM", f"{pattern_name} מתכנס: מחכים לפריצה מאושרת.", lines=lines)


def _wedge_setup(df: pd.DataFrame, timeframe: str) -> ChartAnalysis | None:
    window = df.tail(70)
    if len(window) < 45:
        return None

    high_slope, high_intercept = _fit_line(window["high"])
    low_slope, low_intercept = _fit_line(window["low"])
    start_gap = abs(float(high_intercept - low_intercept))
    end_resistance = float(high_slope * (len(window) - 1) + high_intercept)
    end_support = float(low_slope * (len(window) - 1) + low_intercept)
    end_gap = abs(end_resistance - end_support)
    if start_gap <= 0 or end_gap >= start_gap * 0.75:
        return None

    price = float(window["close"].iloc[-1])
    height = max(start_gap, float(df["atr_14"].iloc[-1]) * 2)
    x0 = window.index[0]
    x1 = window.index[-1]
    lines = [
        OverlayLine("Wedge Resistance", "segment", "#f97316", float(high_intercept), end_resistance, x0, x1),
        OverlayLine("Wedge Support", "segment", "#22c55e", float(low_intercept), end_support, x0, x1),
    ]

    if high_slope < 0 and low_slope < 0 and abs(high_slope) > abs(low_slope):
        if price > end_resistance:
            target = price + height
            eta = target_eta_label(df, price, target, timeframe)
            return _apply_volume_confirmation(df, ChartAnalysis("BUY", "HIGH", f"Falling Wedge נפרץ מעלה. יעד משוער: {eta}.", lines=lines + _entry_target_stop(price, target, end_support, eta), target_eta_label=eta))
        return ChartAnalysis("WAIT", "MEDIUM", "Falling Wedge אפשרי: מחכים לפריצה מעלה.", lines=lines)

    if high_slope > 0 and low_slope > 0 and low_slope > high_slope:
        if price < end_support:
            target = price - height
            eta = target_eta_label(df, price, target, timeframe)
            return _apply_volume_confirmation(df, ChartAnalysis("SELL", "HIGH", f"Rising Wedge נשבר מטה. יעד משוער: {eta}.", lines=lines + _entry_target_stop(price, target, end_resistance, eta), target_eta_label=eta))
        return ChartAnalysis("WAIT", "MEDIUM", "Rising Wedge אפשרי: מחכים לשבירה מטה.", lines=lines)

    return None


def _rectangle_setup(df: pd.DataFrame, timeframe: str) -> ChartAnalysis | None:
    window = df.tail(50)
    resistance = float(window["high"].quantile(0.92))
    support = float(window["low"].quantile(0.08))
    height = resistance - support
    if height <= 0:
        return None
    if height / float(window["close"].iloc[-1]) > 0.08:
        return None

    latest = float(window["close"].iloc[-1])
    atr_value = float(df["atr_14"].iloc[-1])
    touches_resistance = int((window["high"] >= resistance - atr_value * 0.35).sum())
    touches_support = int((window["low"] <= support + atr_value * 0.35).sum())
    if touches_resistance < 2 or touches_support < 2:
        return None

    lines = [
        OverlayLine("Rectangle Resistance", "horizontal", "#f97316", resistance),
        OverlayLine("Rectangle Support", "horizontal", "#22c55e", support),
    ]
    if latest > resistance:
        return _manual_signal(df, timeframe, "BUY", "MEDIUM", "פריצה מעל תעלת דשדוש.", latest, support, support, lines)
    if latest < support:
        return _manual_signal(df, timeframe, "SELL", "MEDIUM", "שבירה מתחת לתעלת דשדוש.", latest, resistance, resistance, lines)

    position = (latest - support) / max(height, 1e-9)
    if position >= 0.8 or position <= 0.2:
        edge = "התנגדות" if position >= 0.8 else "תמיכה"
        return ChartAnalysis(
            "WAIT",
            "MEDIUM",
            f"המחיר קרוב ל{edge} של תעלת דשדוש ({position:.0%} בתוך הטווח): מחכים לפריצה או דחייה.",
            lines=lines,
        )
    return None


def _flag_setup(df: pd.DataFrame, timeframe: str) -> ChartAnalysis | None:
    if len(df) < 70:
        return None
    pole = df.iloc[-55:-24]
    flag = df.tail(24)
    pole_move = float(pole["close"].iloc[-1] - pole["close"].iloc[0])
    atr_value = float(df["atr_14"].iloc[-1])
    if abs(pole_move) < atr_value * 4:
        return None

    x = np.arange(len(flag))
    high_slope, high_intercept = np.polyfit(x, flag["high"], 1)
    low_slope, low_intercept = np.polyfit(x, flag["low"], 1)
    last_support = float(low_slope * (len(flag) - 1) + low_intercept)
    last_resistance = float(high_slope * (len(flag) - 1) + high_intercept)
    latest = float(flag["close"].iloc[-1])
    lines = _trend_channel(df)

    if pole_move < 0 and high_slope > 0 and low_slope > 0:
        if latest < last_support:
            target = latest - abs(pole_move)
            stop = max(last_resistance, float(flag["high"].max()))
            eta = target_eta_label(df, latest, target, timeframe)
            return _apply_volume_confirmation(df, ChartAnalysis("SELL", "HIGH", f"Bearish Flag נשבר מטה. יעד משוער: {eta}.", lines=lines + _entry_target_stop(latest, target, stop, eta), target_eta_label=eta))
        return ChartAnalysis("WAIT", "MEDIUM", "Bearish Flag אפשרי: מחכים לשבירת התמיכה.", lines=lines)

    if pole_move > 0 and high_slope < 0 and low_slope < 0:
        if latest > last_resistance:
            target = latest + abs(pole_move)
            stop = min(last_support, float(flag["low"].min()))
            eta = target_eta_label(df, latest, target, timeframe)
            return _apply_volume_confirmation(df, ChartAnalysis("BUY", "HIGH", f"Bullish Flag נפרץ מעלה. יעד משוער: {eta}.", lines=lines + _entry_target_stop(latest, target, stop, eta), target_eta_label=eta))
        return ChartAnalysis("WAIT", "MEDIUM", "Bullish Flag אפשרי: מחכים לפריצת ההתנגדות.", lines=lines)

    return None


def _market_context(df: pd.DataFrame, lines: list[OverlayLine]) -> ChartAnalysis:
    close = float(df["close"].iloc[-1])
    support = float(df["low"].tail(40).min())
    resistance = float(df["high"].tail(40).max())
    rsi_value = float(df["rsi_14"].iloc[-1])
    sma_20 = float(df["sma_20"].iloc[-1])
    sma_50 = float(df["sma_50"].iloc[-1])
    trend_slope, _ = _fit_line(df["close"].tail(50))
    trend_pct = trend_slope / max(close, 1e-9)

    if close > sma_20 > sma_50 and trend_pct > 0:
        trend = "מגמת עליה"
    elif close < sma_20 < sma_50 and trend_pct < 0:
        trend = "מגמת ירידה"
    else:
        trend = "דשדוש / מעבר בין מגמות"

    range_size = max(resistance - support, 1e-9)
    support_distance = (close - support) / range_size
    resistance_distance = (resistance - close) / range_size

    if rsi_value >= 70:
        momentum = "RSI גבוה, יש סיכון לתיקון"
    elif rsi_value <= 30:
        momentum = "RSI נמוך, יש סיכוי לריבאונד"
    elif rsi_value >= 55:
        momentum = "מומנטום חיובי מתון"
    elif rsi_value <= 45:
        momentum = "מומנטום שלילי מתון"
    else:
        momentum = "מומנטום ניטרלי"

    if resistance_distance < 0.2:
        location = f"המחיר קרוב להתנגדות ({resistance_distance:.0%} מהקצה העליון), מחכים לפריצה לפני כניסה"
    elif support_distance < 0.2:
        location = f"המחיר קרוב לתמיכה ({support_distance:.0%} מהקצה התחתון), שבירה מטה תהיה סימן חולשה"
    else:
        location = f"המחיר באמצע הטווח ({support_distance:.0%} מהתמיכה), אין יתרון ברור לכניסה"

    return ChartAnalysis(
        "WAIT",
        "LOW",
        f"{trend}. {momentum} (RSI {rsi_value:.1f}). {location}.",
        lines=lines,
    )


def _manual_signal(df: pd.DataFrame, timeframe: str, action: str, confidence: str, reason: str, latest: float, boundary: float, stop_reference: float, lines: list[OverlayLine]) -> ChartAnalysis:
    move = abs(latest - boundary)
    if move == 0:
        move = latest * 0.01
    if action == "BUY":
        target = latest + move * 2
        stop = min(stop_reference, latest - move)
    else:
        target = latest - move * 2
        stop = max(stop_reference, latest + move)
    eta = target_eta_label(df, latest, target, timeframe)
    return _apply_volume_confirmation(
        df,
        ChartAnalysis(action, confidence, f"{reason} יעד משוער: {eta}.", lines=lines + _entry_target_stop(latest, target, stop, eta), target_eta_label=eta),
    )


def _apply_volume_confirmation(df: pd.DataFrame, analysis: ChartAnalysis) -> ChartAnalysis:
    ratio = _volume_ratio(df)
    if ratio is None:
        return analysis

    if ratio >= 1.5:
        confidence = "HIGH"
        note = f" נפח הפריצה חזק: {ratio:.2f}x מהממוצע."
    else:
        confidence = "LOW"
        note = f" אזהרה: נפח הפריצה חלש ({ratio:.2f}x מהממוצע), ייתכן שזו פריצת שווא."

    return ChartAnalysis(
        action=analysis.action,
        confidence=confidence,
        reason=analysis.reason + note,
        signal=analysis.signal,
        lines=analysis.lines,
        target_eta_label=analysis.target_eta_label,
        volume_ratio=ratio,
    )


def _volume_ratio(df: pd.DataFrame) -> float | None:
    if "volume" not in df or len(df) < 22:
        return None
    previous_volume = df["volume"].iloc[-21:-1].replace(0, np.nan).mean()
    current_volume = float(df["volume"].iloc[-1])
    if pd.isna(previous_volume) or previous_volume <= 0:
        return None
    return current_volume / float(previous_volume)


def _entry_target_stop(entry: float, target: float, stop: float, target_eta_label: str | None = None) -> list[OverlayLine]:
    target_label = "Target"
    if target_eta_label:
        target_label = f"Target ({target_eta_label})"
    return [
        OverlayLine("Entry", "horizontal", "#38bdf8", entry, dash="solid"),
        OverlayLine(target_label, "horizontal", "#22c55e", target, dash="solid"),
        OverlayLine("Stop Loss", "horizontal", "#ef4444", stop, dash="solid"),
    ]


def _fit_line(series: pd.Series) -> tuple[float, float]:
    x = np.arange(len(series))
    slope, intercept = np.polyfit(x, series, 1)
    return float(slope), float(intercept)


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
