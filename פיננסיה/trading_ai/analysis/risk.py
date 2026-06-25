from __future__ import annotations

from trading_ai.analysis.patterns import PatternMatch
from trading_ai.models import Direction, TradeSignal


def build_signal(symbol: str, timeframe: str, pattern: PatternMatch, min_risk_reward: float) -> TradeSignal | None:
    entry = pattern.breakout_price
    measured_move = max(pattern.measured_move, 0.00000001)

    if pattern.direction == Direction.LONG:
        target = entry + measured_move
        stop_loss = min(pattern.last_swing, entry - measured_move / min_risk_reward)
        risk = entry - stop_loss
        reward = target - entry
    else:
        target = entry - measured_move
        stop_loss = max(pattern.last_swing, entry + measured_move / min_risk_reward)
        risk = stop_loss - entry
        reward = entry - target

    if risk <= 0:
        return None
    risk_reward = reward / risk
    if risk_reward < min_risk_reward:
        return None

    return TradeSignal(
        symbol=symbol,
        timeframe=timeframe,
        pattern=pattern.name,
        direction=pattern.direction,
        entry=float(entry),
        target=float(target),
        stop_loss=float(stop_loss),
        risk_reward=float(risk_reward),
        created_at=pattern.index.to_pydatetime(),
    )

