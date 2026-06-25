from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class MarketDataProvider(ABC):
    @abstractmethod
    def get_ohlcv(self, symbol: str, interval: str, period: str) -> pd.DataFrame:
        """Return OHLCV candles indexed by timestamp."""


def normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    rename_map = {name: name.lower() for name in df.columns}
    df = df.rename(columns=rename_map)

    required = ["open", "high", "low", "close", "volume"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {', '.join(missing)}")

    clean = df[required].dropna().copy()
    clean.index.name = "timestamp"
    return clean

