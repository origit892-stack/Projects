from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

DEFAULT_WATCHLIST = [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "ADA/USDT",
    "DOGE/USDT",
    "AVAX/USDT",
    "LINK/USDT",
    "DOT/USDT",
    "MATIC/USDT",
    "LTC/USDT",
    "NVDA",
    "GLD",
    "MSFT",
    "^GSPC",
    "^TA125.TA",
]


def _csv(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    provider: str = os.getenv("DATA_PROVIDER", "auto")
    watchlist: list[str] = field(default_factory=lambda: _csv(os.getenv("WATCHLIST"), DEFAULT_WATCHLIST))
    timeframes: list[str] = field(default_factory=lambda: _csv(os.getenv("TIMEFRAMES") or os.getenv("INTERVAL"), ["15m"]))
    lookback_period: str = os.getenv("LOOKBACK_PERIOD", "60d")
    scan_every_seconds: int = int(os.getenv("SCAN_EVERY_SECONDS", "300"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///trading_ai.db")
    telegram_bot_token: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = os.getenv("TELEGRAM_CHAT_ID")
    min_risk_reward: float = float(os.getenv("MIN_RISK_REWARD", "2.0"))

    @property
    def interval(self) -> str:
        return self.timeframes[0]
