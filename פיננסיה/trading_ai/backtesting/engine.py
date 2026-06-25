from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from trading_ai.analysis.engine import AnalysisEngine
from trading_ai.analysis.indicators import add_indicators
from trading_ai.models import Direction


@dataclass(frozen=True)
class BacktestReport:
    trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
    net_r: float


def run_backtest(symbol: str, timeframe: str, candles: pd.DataFrame, min_risk_reward: float = 2.0) -> BacktestReport:
    engine = AnalysisEngine(min_risk_reward)
    prepared = add_indicators(candles).dropna()
    outcomes: list[float] = []
    equity = [0.0]

    for i in range(80, len(prepared) - 1):
        window = prepared.iloc[:i]
        signal = engine.analyze(symbol, timeframe, window)
        if not signal:
            continue

        future = prepared.iloc[i : min(i + 80, len(prepared))]
        result = _resolve_trade(signal.direction, signal.target, signal.stop_loss, future)
        if result is None:
            continue
        outcomes.append(result)
        equity.append(equity[-1] + result)

    if not outcomes:
        return BacktestReport(0, 0.0, 0.0, 0.0, 0.0)

    wins = [item for item in outcomes if item > 0]
    losses = [abs(item) for item in outcomes if item < 0]
    profit_factor = sum(wins) / sum(losses) if losses else float("inf")
    return BacktestReport(
        trades=len(outcomes),
        win_rate=len(wins) / len(outcomes),
        profit_factor=profit_factor,
        max_drawdown=_max_drawdown(equity),
        net_r=sum(outcomes),
    )


def _resolve_trade(direction: Direction, target: float, stop_loss: float, future: pd.DataFrame) -> float | None:
    for _, row in future.iterrows():
        if direction == Direction.LONG:
            if row["low"] <= stop_loss:
                return -1.0
            if row["high"] >= target:
                return 2.0
        else:
            if row["high"] >= stop_loss:
                return -1.0
            if row["low"] <= target:
                return 2.0
    return None


def _max_drawdown(equity: list[float]) -> float:
    peak = equity[0]
    drawdown = 0.0
    for value in equity:
        peak = max(peak, value)
        drawdown = min(drawdown, value - peak)
    return abs(drawdown)

