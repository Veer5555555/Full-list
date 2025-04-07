import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# List of NSE stock symbols
symbols = [
    'INFY.NS', 'WIPRO.NS', 'TCS.NS', 'SBIN.NS', 'LICI.NS', 'ADANIPORTS.NS', 'TATAMOTORS.NS',
    'TATASTEEL.NS', 'HAL.NS', 'IRCTC.NS', 'IOC.NS', 'COALINDIA.NS', 'HINDUNILVR.NS',
    'PNB.NS', 'RELIANCE.NS', 'ITC.NS', 'VEDL.NS', 'JSWSTEEL.NS', 'NTPC.NS', 'POWERGRID.NS',
    'BPCL.NS', 'ONGC.NS', 'NHPC.NS', 'ADANIGREEN.NS', 'GAIL.NS', 'TECHM.NS', 'HCLTECH.NS',
    'CIPLA.NS', 'DIVISLAB.NS', 'SUNPHARMA.NS', 'BAJAJFINSV.NS', 'BAJFINANCE.NS',
    'MARUTI.NS', 'EICHERMOT.NS', 'M&M.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'AXISBANK.NS',
    'BANKBARODA.NS', 'INDUSINDBK.NS', 'IDFCFIRSTB.NS', 'FEDERALBNK.NS', 'CANBK.NS',
    'UNIONBANK.NS', 'NAUKRI.NS', 'PAYTM.NS', 'ZOMATO.NS', 'DELHIVERY.NS', 'TATAPOWER.NS',
    'UPL.NS', 'LT.NS', 'SBICARD.NS', 'INDIGO.NS', 'BHARTIARTL.NS', 'IDEA.NS', 'BEL.NS',
    'TITAN.NS', 'DMART.NS', 'ASIANPAINT.NS', 'DIXON.NS', 'ABB.NS', 'BHEL.NS', 'IRFC.NS',
    'RVNL.NS', 'PFC.NS', 'RECLTD.NS', 'SJVN.NS', 'HFCL.NS', 'TATACHEM.NS', 'HDFCLIFE.NS',
    'ICICIPRULI.NS', 'ICICIGI.NS', 'SBILIFE.NS', 'HDFCAMC.NS', 'CHOLAFIN.NS',
    'MUTHOOTFIN.NS', 'LTIM.NS', 'PERSISTENT.NS', 'COFORGE.NS', 'NESTLEIND.NS',
    'COLPAL.NS', 'GODREJCP.NS', 'MARICO.NS', 'BRITANNIA.NS', 'HAVELLS.NS', 'BLUEDART.NS',
    'DRREDDY.NS', 'AUROPHARMA.NS', 'GLAND.NS', 'LUPIN.NS', 'BIOCON.NS', 'BOSCHLTD.NS',
    'ESCORTS.NS', 'ASHOKLEY.NS', 'TIINDIA.NS', 'SRF.NS', 'DEEPAKNTR.NS', 'PIIND.NS',
    'ASTRAL.NS', 'TATVA.NS', 'ADANIENT.NS', 'VBL.NS', 'SIEMENS.NS', 'KPRMILL.NS',
    'AIAENG.NS', 'POLYCAB.NS', 'INDUSTOWER.NS', 'KALYANKJIL.NS'
]

RSI_PERIOD = 14

@st.cache_data(ttl=3600)
def fetch_data(symbol):
    df = yf.download(symbol, period="3mo", interval="1d")
    if df.empty or "Close" not in df:
        return None
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["MACD"] = df["Close"].ewm(span=12).mean() - df["Close"].ewm(span=26).mean()
    df["Signal"] = df["MACD"].ewm(span=9).mean()
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(RSI_PERIOD).mean()
    avg_loss = loss.rolling(RSI_PERIOD).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    df["MACD_diff"] = df["MACD"] - df["Signal"]
    df["GANN_LEVEL"] = (df["Close"] / 10).round() * 10
    df.dropna(inplace=True)
    return df

def analyze(df):
    if df is None or df.empty:
        return "❌ Error", "-", "-", "-", "-", "-", "-"
    close = df["Close"].iloc[-1]
    rsi = df["RSI"].iloc[-1]
    macd_diff = df["MACD_diff"].iloc[-1]
    ema20 = df["EMA20"].iloc[-1]
    ema50 = df["EMA50"].iloc[-1]

    bullish = close > ema20 > ema50 and macd_diff > 0 and rsi > 50
    bearish = close < ema20 < ema50 and macd_diff < 0 and rsi < 50

    if bullish and rsi < 70:
        signal = "🟢 Strong Bullish"
    elif bearish and rsi > 30:
        signal = "🔴 Strong Bearish"
    elif bullish:
        signal = "🟡 Mild Bullish"
    elif bearish:
        signal = "🟠 Mild Bearish"
    else:
        signal = "⚪ Neutral"

    target1 = round(close * 1.02, 2)
    target2 = round(close * 1.04, 2)
    target3 = round(close * 1.06, 2)
    stoploss = round(close * 0.97, 2)

    return signal, round(close, 2), round(rsi, 2), target1, target2, target3, stoploss

# Streamlit app layout
st.set_page_config(page_title="📈 Stock Trend Dashboard", layout="wide")
st.title("📊 Indian Stock Breakout & Sentiment Dashboard")
st.markdown("Live trend detection using EMA, MACD, RSI, and GANN analysis")

rows = []
for symbol in symbols:
    try:
        df = fetch_data(symbol)
        signal, price, rsi, t1, t2, t3, sl = analyze(df)
        rows.append({
            "Symbol": symbol,
            "Signal": signal,
            "Price": price,
            "RSI": rsi,
            "Target 1": t1,
            "Target 2": t2,
            "Target 3": t3,
            "Stop Loss": sl
        })
    except Exception as e:
        st.warning(f"⚠️ Error with {symbol}: {e}")

df_final = pd.DataFrame(rows)
if df_final.empty:
    st.error("🚫 No data to display. Check your internet or stock symbols.")
else:
    st.dataframe(df_final, use_container_width=True)
