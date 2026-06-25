from __future__ import annotations

import logging

import pandas as pd
import yfinance as yf

from trading_ai.data.base import MarketDataProvider, normalize_ohlcv

logger = logging.getLogger(__name__)


class YFinanceProvider(MarketDataProvider):
    def get_ohlcv(self, symbol: str, interval: str, period: str) -> pd.DataFrame:
        logger.info("Downloading %s candles interval=%s period=%s", symbol, interval, period)
        df = yf.download(symbol, interval=interval, period=period, progress=False, auto_adjust=False)
        if df.empty:
            raise ValueError(f"No data returned for {symbol}")
        return normalize_ohlcv(df)

