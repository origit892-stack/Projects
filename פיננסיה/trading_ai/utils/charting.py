from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from trading_ai.models import TradeSignal


def render_signal_chart(candles: pd.DataFrame, signal: TradeSignal, output_dir: str = "charts") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    path = Path(output_dir) / f"{signal.symbol.replace('/', '-')}_{signal.timeframe}_{signal.created_at:%Y%m%d_%H%M%S}.png"

    tail = candles.tail(120)
    plt.figure(figsize=(12, 6))
    plt.plot(tail.index, tail["close"], label="Close", color="black", linewidth=1.4)
    plt.axhline(signal.entry, label="Entry", color="#2563eb", linestyle="--")
    plt.axhline(signal.target, label="Target", color="#16a34a", linestyle="--")
    plt.axhline(signal.stop_loss, label="Stop Loss", color="#dc2626", linestyle="--")
    plt.title(f"{signal.symbol} {signal.timeframe} - {signal.pattern} {signal.direction.value}")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return str(path)

