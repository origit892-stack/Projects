from __future__ import annotations

import asyncio
import logging

from trading_ai.analysis.engine import AnalysisEngine
from trading_ai.config import Settings
from trading_ai.data.factory import create_provider
from trading_ai.notifications.telegram import TelegramNotifier
from trading_ai.storage.database import Database, save_signal, update_active_signals
from trading_ai.utils.charting import render_signal_chart

logger = logging.getLogger(__name__)


class Scanner:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.provider = create_provider(settings.provider)
        self.engine = AnalysisEngine(settings.min_risk_reward)
        self.db = Database(settings.database_url)
        self.notifier = TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id)

    async def scan_once(self) -> None:
        self.db.create_all()
        for symbol in self.settings.watchlist:
            for timeframe in self.settings.timeframes:
                try:
                    candles = self.provider.get_ohlcv(symbol, timeframe, self.settings.lookback_period)
                    latest_price = float(candles["close"].iloc[-1])
                    with self.db.session() as session:
                        update_active_signals(session, symbol, latest_price)

                    signal = self.engine.analyze(symbol, timeframe, candles)
                    if not signal:
                        logger.info("No signal for %s %s", symbol, timeframe)
                        continue

                    chart_path = render_signal_chart(candles, signal)
                    signal = signal.__class__(**{**signal.__dict__, "chart_path": chart_path})
                    with self.db.session() as session:
                        is_new = save_signal(session, signal)

                    if is_new:
                        logger.info("New signal: %s", signal)
                        await self.notifier.send_signal(signal)
                except Exception:
                    logger.exception("Failed scanning %s %s", symbol, timeframe)

    async def run_forever(self) -> None:
        while True:
            await self.scan_once()
            await asyncio.sleep(self.settings.scan_every_seconds)
