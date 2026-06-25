from __future__ import annotations

import pandas as pd

from trading_ai.data.base import MarketDataProvider
from trading_ai.data.binance_provider import BinanceProvider
from trading_ai.data.yfinance_provider import YFinanceProvider


class AutoProvider(MarketDataProvider):
    def __init__(self) -> None:
        self.binance = BinanceProvider()
        self.yfinance = YFinanceProvider()

    def get_ohlcv(self, symbol: str, interval: str, period: str) -> pd.DataFrame:
        if "/" in symbol:
            return self.binance.get_ohlcv(symbol, interval, period)
        return self.yfinance.get_ohlcv(symbol, _to_yfinance_interval(interval), period)


def _to_yfinance_interval(interval: str) -> str:
    supported = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"}
    if interval in supported:
        return interval
    if interval == "4h":
        return "1h"
    return interval
