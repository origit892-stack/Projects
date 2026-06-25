# AI Trading Scanner

מערכת Python מודולרית לסריקת נכסים בזמן אמת, זיהוי תבניות טכניות, יצירת איתותי Entry / Target / Stop-Loss, שמירה למסד נתונים, Backtesting ושליחת התראות Telegram.

> אין לראות בפרויקט ייעוץ השקעות. יש לבדוק כל אסטרטגיה בסביבת Paper Trading לפני שימוש בכסף אמיתי.

## התקנה

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

ברירת המחדל משתמשת ב-`DATA_PROVIDER=auto`: זוגות קריפטו כמו `BTC/USDT` נמשכים מ-Binance, ומניות/מדדים כמו `NVDA`, `MSFT`, `GLD`, `^GSPC`, `^TA125.TA` נמשכים מ-Yahoo Finance.
אפשר לעבור ל-PostgreSQL דרך `DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/trading_ai`.
ב-Yahoo Finance, נתונים תוך-יומיים כמו `15m` מוגבלים היסטורית; ל-Backtest של שנתיים השתמשו למשל ב-`TIMEFRAMES=1d`, או השאירו `DATA_PROVIDER=binance` עבור זוגות קריפטו כמו `BTC/USDT`.

## הרצה

סריקה חד-פעמית:

```bash
python3 bot.py scan-once
```

סריקה רציפה כל `SCAN_EVERY_SECONDS`:

```bash
python3 bot.py run
```

Backtest על שנתיים:

```bash
python3 bot.py backtest --symbol BTC/USDT --timeframe 1h --period 60d
```

## מבנה

- `trading_ai/data` - ספקי נתונים: Yahoo Finance ו-Binance דרך ccxt.
- `trading_ai/analysis` - אינדיקטורים, זיהוי תבניות וניהול סיכון.
- `trading_ai/storage` - SQLAlchemy לשמירת איתותים ועדכון סטטוס עסקאות.
- `trading_ai/notifications` - Telegram Bot API.
- `trading_ai/backtesting` - סימולטור ביצועים עם Win Rate, Profit Factor, Max Drawdown ו-Net R.

## ברירת מחדל לסריקה

הסורק עובר על כל שילוב של מטבע וטיימפריים מתוך `.env`:

```env
DATA_PROVIDER=auto
WATCHLIST=BTC/USDT,ETH/USDT,BNB/USDT,SOL/USDT,XRP/USDT,ADA/USDT,DOGE/USDT,AVAX/USDT,LINK/USDT,DOT/USDT,MATIC/USDT,LTC/USDT,NVDA,GLD,MSFT,^GSPC,^TA125.TA
TIMEFRAMES=15m,1h
LOOKBACK_PERIOD=60d
```

הגדרת `INTERVAL=15m` עדיין נתמכת לאחור, אבל `TIMEFRAMES` מאפשרת לסרוק כמה מרווחים באותה ריצה.

## תבניות נתמכות כרגע

- Bullish Flag / Bearish Flag.
- Head and Shoulders.
- Support / Resistance Breakouts.
- Bollinger Band breakout / breakdown כטריגר משני.
- כפתור הדשבורד מוסיף גם Double Top/Bottom, Rectangles, Triangles, Wedges וקווי Fibonacci Retracement.
