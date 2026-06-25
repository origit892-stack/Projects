from __future__ import annotations

import time

import pandas as pd
import ccxt

from trading_ai.data.base import MarketDataProvider, normalize_ohlcv


class BinanceProvider(MarketDataProvider):
    def __init__(self) -> None:
        self.exchange = ccxt.binance({"enableRateLimit": True})

    def get_ohlcv(self, symbol: str, interval: str, period: str) -> pd.DataFrame:
        rows = self._fetch_paginated(symbol, interval, period)
        if not rows:
            raise ValueError(f"No data returned for {symbol}")
        df = pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").set_index("timestamp")
        return normalize_ohlcv(df)

    def _fetch_paginated(self, symbol: str, interval: str, period: str) -> list[list[float]]:
        timeframe_ms = self.exchange.parse_timeframe(interval) * 1000
        now_ms = self.exchange.milliseconds()
        since = now_ms - _period_to_milliseconds(period)
        all_rows: list[list[float]] = []

        while since < now_ms:
            rows = self.exchange.fetch_ohlcv(symbol, timeframe=interval, since=since, limit=1000)
            if not rows:
                break

            all_rows.extend(rows)
            next_since = int(rows[-1][0]) + timeframe_ms
            if next_since <= since:
                break
            since = next_since

            if len(rows) < 1000:
                break
            time.sleep(self.exchange.rateLimit / 1000)

        return all_rows


def _period_to_milliseconds(period: str) -> int:
    unit = period[-1]
    amount = int(period[:-1])
    multipliers = {
        "m": 60 * 1000,
        "h": 60 * 60 * 1000,
        "d": 24 * 60 * 60 * 1000,
        "w": 7 * 24 * 60 * 60 * 1000,
    }
    if unit not in multipliers:
        raise ValueError(f"Unsupported period: {period}. Use values like 12h, 60d, 2w.")
    return amount * multipliers[unit]
