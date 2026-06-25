from __future__ import annotations

import argparse
import asyncio
import logging

from trading_ai.backtesting.engine import run_backtest
from trading_ai.config import Settings
from trading_ai.data.factory import create_provider
from trading_ai.scanner import Scanner


def main() -> None:
    parser = argparse.ArgumentParser(description="AI trading scanner")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("scan-once")
    subparsers.add_parser("run")
    backtest = subparsers.add_parser("backtest")
    backtest.add_argument("--symbol", default=None)
    backtest.add_argument("--timeframe", default=None)
    backtest.add_argument("--period", default="730d")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    settings = Settings()

    if args.command == "scan-once":
        asyncio.run(Scanner(settings).scan_once())
    elif args.command == "run":
        asyncio.run(Scanner(settings).run_forever())
    elif args.command == "backtest":
        symbol = args.symbol or settings.watchlist[0]
        timeframe = args.timeframe or settings.interval
        provider = create_provider(settings.provider)
        candles = provider.get_ohlcv(symbol, timeframe, args.period)
        report = run_backtest(symbol, timeframe, candles, settings.min_risk_reward)
        print(f"Trades: {report.trades}")
        print(f"Win Rate: {report.win_rate:.2%}")
        print(f"Profit Factor: {report.profit_factor:.2f}")
        print(f"Max Drawdown: {report.max_drawdown:.2f}R")
        print(f"Net: {report.net_r:.2f}R")


if __name__ == "__main__":
    main()
