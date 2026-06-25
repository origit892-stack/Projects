import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from typing import Optional

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

from trading_ai.analysis.chart_overlay import ChartAnalysis, analyze_chart
from trading_ai.config import Settings
from trading_ai.data.factory import create_provider

# עיצוב בסיסי של האתר
st.set_page_config(page_title="AI Trading Dashboard", layout="wide")
st.title("📊 AI Trading Bot - ממשק ניהול גרפי")
settings = Settings()
provider = create_provider(settings.provider)

if "auto_analyze" not in st.session_state:
    st.session_state.auto_analyze = True
if "force_analyze_once" not in st.session_state:
    st.session_state.force_analyze_once = False


def enable_auto_analysis() -> None:
    st.session_state.auto_analyze = True
    st.session_state.force_analyze_once = True


# התחברות למסד הנתונים של הבוט
def load_signals():
    try:
        conn = sqlite3.connect("trading_ai.db")
        # שנה את שם הטבלה אם בבוט שלך היא נקראת אחרת (למשל signals)
        df = pd.read_sql_query("SELECT * FROM signals", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame() # מחזיר טבלה ריקה אם עוד אין איתותים

# תפריט צדדי לבחירת נכס
symbol = st.sidebar.selectbox("בחר נכס לצפייה:", settings.watchlist)
timeframe = st.sidebar.selectbox("טיימפריים:", settings.timeframes)
period = st.sidebar.selectbox("טווח זמן לגרף:", ["2d", "7d", "30d", "60d"])
refresh_seconds = st.sidebar.number_input("רענון חי כל X שניות", min_value=0, max_value=3600, value=60, step=10)
if refresh_seconds > 0 and st_autorefresh:
    st_autorefresh(interval=refresh_seconds * 1000, key="live_refresh")
elif refresh_seconds > 0:
    st.sidebar.warning("להפעלת רענון אוטומטי התקן streamlit-autorefresh.")

st.sidebar.checkbox("ניתוח אוטומטי בכל רענון", key="auto_analyze")
st.sidebar.button("נתח מצב גרף עכשיו", use_container_width=True, on_click=enable_auto_analysis)

st.subheader(f"📈 גרף נתוני שוק עבור {symbol} ({timeframe})")

# משיכת נתוני הגרף העדכניים
with st.spinner("טוען נתונים מהבורסה..."):
    try:
        data = provider.get_ohlcv(symbol, timeframe, period)
    except Exception as exc:
        st.error(f"לא הצלחנו לטעון נתונים עבור {symbol}: {exc}")
        data = pd.DataFrame()


def candle_x_values(candles: pd.DataFrame) -> list[str]:
    return [pd.Timestamp(value).strftime("%Y-%m-%d %H:%M") for value in candles.index]


def line_x_value(value: Optional[pd.Timestamp]) -> Optional[str]:
    if value is None:
        return None
    return pd.Timestamp(value).strftime("%Y-%m-%d %H:%M")


def add_analysis_overlay(fig: go.Figure, analysis: ChartAnalysis, candles: pd.DataFrame) -> None:
    x_values = candle_x_values(candles)
    x0 = x_values[0]
    x1 = x_values[-1]
    for line in analysis.lines:
        if line.kind == "segment" and line.x0 is not None and line.x1 is not None and line.y1 is not None:
            fig.add_trace(
                go.Scatter(
                    x=[line_x_value(line.x0), line_x_value(line.x1)],
                    y=[line.y0, line.y1],
                    mode="lines",
                    line={"color": line.color, "width": 2, "dash": line.dash},
                    name=line.label,
                )
            )
            continue

        fig.add_shape(
            type="line",
            x0=x0,
            x1=x1,
            y0=line.y0,
            y1=line.y0,
            line={"color": line.color, "width": 2, "dash": line.dash},
        )
        fig.add_annotation(
            x=x1,
            y=line.y0,
            text=f"{line.label}: {line.y0:.4f}",
            showarrow=False,
            xanchor="left",
            font={"color": line.color, "size": 12},
        )


analysis = None
should_analyze = st.session_state.get("auto_analyze", True) or st.session_state.pop("force_analyze_once", False)
if should_analyze and not data.empty:
    analysis = analyze_chart(symbol, timeframe, data, settings.min_risk_reward)

if not data.empty:
    x_values = candle_x_values(data)
    # יצירת גרף נרות יפניים אינטראקטיבי
    fig = go.Figure(data=[go.Candlestick(
        x=x_values,
        open=data["open"],
        high=data["high"],
        low=data["low"],
        close=data["close"],
        name="Price"
    )])

    if analysis:
        add_analysis_overlay(fig, analysis, data)
    
    fig.update_layout(
        xaxis={
            "type": "category",
            "rangeslider": {"visible": False},
            "nticks": 8,
        },
        template="plotly_dark",
        height=600,
    )
    st.plotly_chart(fig, use_container_width=True)

    if analysis:
        action_labels = {
            "BUY": "כניסה לקנייה",
            "SELL": "מכירה / שורט",
            "WAIT": "להמתין",
        }
        confidence_labels = {
            "HIGH": "גבוה",
            "MEDIUM": "בינוני",
            "LOW": "נמוך",
        }
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("מצב", action_labels.get(analysis.action, analysis.action))
        col2.metric("ביטחון", confidence_labels.get(analysis.confidence, analysis.confidence))
        if analysis.signal:
            col3.metric("יחס סיכוי/סיכון", f"{analysis.signal.risk_reward:.2f}")
        else:
            col3.metric("יחס סיכוי/סיכון", "-")
        col4.metric("זמן ליעד", analysis.target_eta_label or "-")
        if analysis.volume_ratio is not None:
            st.metric("חוזק פריצה לפי Volume", f"{analysis.volume_ratio:.2f}x", help="נפח הנר האחרון ביחס לממוצע 20 הנרות הקודמים. מעל 1.50x נחשב אישור חזק.")
        st.info(analysis.reason)
else:
    st.error("לא הצלחנו לטעון נתונים עבור הנכס הנבחר.")


@st.cache_data(ttl=60)
def current_price_for_signal(signal_symbol: str, signal_timeframe: str) -> Optional[float]:
    try:
        candles = provider.get_ohlcv(signal_symbol, signal_timeframe or timeframe, "2d")
        if candles.empty:
            return None
        return float(candles["close"].iloc[-1])
    except Exception:
        return None


def add_live_pnl(signals: pd.DataFrame) -> pd.DataFrame:
    enriched = signals.copy()
    current_prices = []
    pnl_values = []

    for _, row in enriched.iterrows():
        signal_symbol = str(row.get("symbol", ""))
        signal_timeframe = str(row.get("timeframe", timeframe))
        entry = float(row.get("entry", 0) or 0)
        direction = str(row.get("direction", "LONG"))
        current_price = current_price_for_signal(signal_symbol, signal_timeframe)
        current_prices.append(current_price)

        if not current_price or entry <= 0:
            pnl_values.append(None)
            continue

        if direction == "SHORT":
            pnl = (entry - current_price) / entry * 100
        else:
            pnl = (current_price - entry) / entry * 100
        pnl_values.append(pnl)

    enriched["current_price"] = current_prices
    enriched["live_pnl_pct"] = pnl_values
    return enriched


def color_pnl(value: Optional[float]) -> str:
    if value is None or pd.isna(value):
        return ""
    if value >= 0:
        return "color: #16a34a; font-weight: 700"
    return "color: #dc2626; font-weight: 700"


# הצגת טבלת האיתותים ההיסטוריים מה-Database
st.subheader("📋 איתותים אחרונים שנשמרו במסד הנתונים")
signals_df = load_signals()

if not signals_df.empty:
    # סינון האיתותים לפי הנכס הנבחר
    filtered_signals = signals_df[signals_df["symbol"] == symbol] if "symbol" in signals_df.columns else signals_df
    enriched_signals = add_live_pnl(filtered_signals)
    styled = enriched_signals.style.applymap(color_pnl, subset=["live_pnl_pct"]) if "live_pnl_pct" in enriched_signals.columns else enriched_signals
    st.dataframe(styled, use_container_width=True)
else:
    st.info("קובץ מסד הנתונים ריק או שעדיין לא נוצרו איתותי קנייה/מכירה בזמן אמת.")
