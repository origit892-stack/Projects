from __future__ import annotations

import logging

from telegram import Bot

from trading_ai.models import TradeSignal

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, token: str | None, chat_id: str | None) -> None:
        self.enabled = bool(token and chat_id)
        self.chat_id = chat_id
        self.bot = Bot(token) if token else None

    async def send_signal(self, signal: TradeSignal) -> None:
        if not self.enabled or not self.bot or not self.chat_id:
            logger.info("Telegram is not configured; skipping notification.")
            return

        text = (
            f"New trading signal\n"
            f"{signal.symbol} | {signal.timeframe}\n"
            f"Pattern: {signal.pattern}\n"
            f"Direction: {signal.direction.value}\n"
            f"Entry: {signal.entry:.4f}\n"
            f"Target: {signal.target:.4f}\n"
            f"Target ETA: {signal.target_eta_label or 'N/A'}\n"
            f"Stop-Loss: {signal.stop_loss:.4f}\n"
            f"Risk/Reward: {signal.risk_reward:.2f}"
        )
        if signal.chart_path:
            with open(signal.chart_path, "rb") as chart:
                await self.bot.send_photo(chat_id=self.chat_id, photo=chart, caption=text)
        else:
            await self.bot.send_message(chat_id=self.chat_id, text=text)
