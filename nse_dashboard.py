import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# All NSE stock symbols you provided
symbols = [ 'INFY.NS', 'WIPRO.NS', 'TCS.NS', 'SBIN.NS', 'LICI.NS', 
    'ADANIPORTS.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'HAL.NS', 'IRCTC.NS',
    'IOC.NS', 'COALINDIA.NS', 'HINDUNILVR.NS', 'PNB.NS', 'RELIANCE.NS',
    'ITC.NS', 'VEDL.NS', 'JSWSTEEL.NS', 'NTPC.NS', 'POWERGRID.NS',
    'BPCL.NS', 'ONGC.NS', 'NHPC.NS', 'ADANIGREEN.NS', 'GAIL.NS', 'TECHM.NS',
    'HCLTECH.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'SUNPHARMA.NS', 'BAJAJFINSV.NS',
    'BAJFINANCE.NS', 'MARUTI.NS', 'EICHERMOT.NS', 'M&M.NS', 'HDFCBANK.NS',
    'ICICIBANK.NS', 'AXISBANK.NS', 'BANKBARODA.NS', 'INDUSINDBK.NS', 'IDFCFIRSTB.NS',
    'FEDERALBNK.NS', 'CANBK.NS', 'UNIONBANK.NS', 'NAUKRI.NS', 'PAYTM.NS',
    'ZOMATO.NS', 'DELHIVERY.NS', 'TATAPOWER.NS', 'UPL.NS', 'LT.NS',
    'SBICARD.NS', 'INDIGO.NS', 'BHARTIARTL.NS', 'IDEA.NS', 'BEL.NS',
    'TITAN.NS', 'DMART.NS', 'ASIANPAINT.NS', 'DIXON.NS', 'ABB.NS',
    'BHEL.NS', 'IRFC.NS', 'RVNL.NS', 'PFC.NS', 'RECLTD.NS', 'SJVN.NS',
    'HFCL.NS', 'TATACHEM.NS', 'HDFCLIFE.NS', 'ICICIPRULI.NS', 'ICICIGI.NS',
    'SBILIFE.NS', 'HDFCAMC.NS', 'CHOLAFIN.NS', 'MUTHOOTFIN.NS', 'LTIM.NS',
    'PERSISTENT.NS', 'COFORGE.NS', 'NESTLEIND.NS', 'COLPAL.NS', 'GODREJCP.NS',
    'MARICO.NS', 'BRITANNIA.NS', 'HAVELLS.NS', 'BLUEDART.NS', 'DRREDDY.NS',
    'AUROPHARMA.NS', 'GLAND.NS', 'LUPIN.NS', 'BIOCON.NS', 'BOSCHLTD.NS',
    'ESCORTS.NS', 'ASHOKLEY.NS', 'TIINDIA.NS', 'SRF.NS', 'DEEPAKNTR.NS',
    'PIIND.NS', 'ASTRAL.NS', 'TATVA.NS', 'ADANIENT.NS', 'VBL.NS', 'SIEMENS.NS',
    'KPRMILL.NS', 'AIAENG.NS', 'POLYCAB.NS', 'INDUSTOWER.NS', 'KALYANKJIL.NS'
]

# Constants
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Streamlit UI
st.set_page_config(layout="wide")
st.title("📈 Indian Stock Market Dashboard")
st.caption("Breakout Detection with RSI, MACD, GANN & Multi-timeframe Sentiment")

# Table to collect all stock data
final_data = []

for symbol in symbols:
    try:
        df = yf.download(symbol, period="3mo", interval="1d")
        if df.empty or len(df) < 60:
            continue

        # Indicators
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
        df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = df["EMA12"] - df["EMA26"]
        df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
        df["MACD_diff"] = df["MACD"] - df["Signal"]

        delta = df["Close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        RS = gain / loss
        df["RSI"] = 100 - (100 / (1 + RS))

        close = df["Close"].iloc[-1]
        ema20 = df["EMA20"].iloc[-1]
        ema50 = df["EMA50"].iloc[-1]
        rsi = df["RSI"].iloc[-1]
        macd_diff = df["MACD_diff"].iloc[-1]

        # Trend logic
        bullish = close > ema20 and ema20 > ema50 and macd_diff > 0 and rsi > 50
        bearish = close < ema20 and ema20 < ema50 and macd_diff < 0 and rsi < 50

        if bullish and rsi < RSI_OVERBOUGHT:
            sentiment = "🟢 Strong Bullish"
        elif bearish and rsi > RSI_OVERSOLD:
            sentiment = "🔴 Strong Bearish"
        elif bullish:
            sentiment = "🟡 Mild Bullish"
        elif bearish:
            sentiment = "🟠 Mild Bearish"
        else:
            sentiment = "⚪ Neutral"

        # Targets and SL (approx levels)
        target1 = round(close * 1.02, 2)
        target2 = round(close * 1.04, 2)
        target3 = round(close * 1.06, 2)
        stop_loss = round(close * 0.97, 2)

        final_data.append({
            "Symbol": symbol,
            "Close": round(close, 2),
            "RSI": round(rsi, 2),
            "MACD Diff": round(macd_diff, 2),
            "EMA20": round(ema20, 2),
            "EMA50": round(ema50, 2),
            "Sentiment": sentiment,
            "Target 1": target1,
            "Target 2": target2,
            "Target 3": target3,
            "Stop Loss": stop_loss,
        })

    except Exception as e:
        st.warning(f"⚠️ Error with {symbol}: {e}")

# Display final table
df_final = pd.DataFrame(final_data)
if not df_final.empty:
    st.dataframe(df_final, use_container_width=True)
else:
    st.error("🚫 No data to display. Check stock symbols or your network connection.")
