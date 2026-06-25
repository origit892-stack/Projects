from __future__ import annotations

import pandas as pd

from trading_ai.analysis.indicators import add_indicators
from trading_ai.analysis.patterns import detect_latest_pattern
from trading_ai.analysis.risk import build_signal
from trading_ai.analysis.target_time import target_eta_label
from trading_ai.models import TradeSignal


class AnalysisEngine:
    def __init__(self, min_risk_reward: float = 2.0) -> None:
        self.min_risk_reward = min_risk_reward

    def analyze(self, symbol: str, timeframe: str, candles: pd.DataFrame) -> TradeSignal | None:
        prepared = add_indicators(candles).dropna()
        pattern = detect_latest_pattern(prepared)
        if not pattern:
            return None
        signal = build_signal(symbol, timeframe, pattern, self.min_risk_reward)
        if not signal:
            return None
        return signal.__class__(
            **{
                **signal.__dict__,
                "target_eta_label": target_eta_label(prepared, signal.entry, signal.target, timeframe),
            }
        )
