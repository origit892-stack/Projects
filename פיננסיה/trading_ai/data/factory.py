from __future__ import annotations

from trading_ai.data.base import MarketDataProvider
from trading_ai.data.auto_provider import AutoProvider
from trading_ai.data.binance_provider import BinanceProvider
from trading_ai.data.yfinance_provider import YFinanceProvider


def create_provider(name: str) -> MarketDataProvider:
    normalized = name.lower()
    if normalized == "auto":
        return AutoProvider()
    if normalized == "yfinance":
        return YFinanceProvider()
    if normalized == "binance":
        return BinanceProvider()
    raise ValueError(f"Unsupported DATA_PROVIDER: {name}")
