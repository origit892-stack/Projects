from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class SignalStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass(frozen=True)
class TradeSignal:
    symbol: str
    timeframe: str
    pattern: str
    direction: Direction
    entry: float
    target: float
    stop_loss: float
    risk_reward: float
    created_at: datetime
    status: SignalStatus = SignalStatus.ACTIVE
    chart_path: str | None = None
    target_eta_label: str | None = None
