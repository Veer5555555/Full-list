import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Constants
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
EMA_SHORT = 12
EMA_LONG = 26
EMA_SIGNAL = 9

# Stock list
symbols = [
    'INFY.NS', 'WIPRO.NS', 'TCS.NS', 'SBIN.NS', 'LICI.NS', 'ADANIPORTS.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'HAL.NS',
    'IRCTC.NS', 'IOC.NS', 'COALINDIA.NS', 'HINDUNILVR.NS', 'PNB.NS', 'RELIANCE.NS', 'ITC.NS', 'VEDL.NS', 'JSWSTEEL.NS',
    'NTPC.NS', 'POWERGRID.NS', 'BPCL.NS', 'ONGC.NS', 'NHPC.NS', 'ADANIGREEN.NS', 'GAIL.NS', 'TECHM.NS', 'HCLTECH.NS',
    'CIPLA.NS', 'DIVISLAB.NS', 'SUNPHARMA.NS', 'BAJAJFINSV.NS', 'BAJFINANCE.NS', 'MARUTI.NS', 'EICHERMOT.NS', 'M&M.NS',
    'HDFCBANK.NS', 'ICICIBANK.NS', 'AXISBANK.NS', 'BANKBARODA.NS', 'INDUSINDBK.NS', 'IDFCFIRSTB.NS', 'FEDERALBNK.NS',
    'CANBK.NS', 'UNIONBANK.NS', 'NAUKRI.NS', 'PAYTM.NS', 'ZOMATO.NS', 'DELHIVERY.NS', 'TATAPOWER.NS', 'UPL.NS', 'LT.NS',
    'SBICARD.NS', 'INDIGO.NS', 'BHARTIARTL.NS', 'IDEA.NS', 'BEL.NS', 'TITAN.NS', 'DMART.NS', 'ASIANPAINT.NS',
    'DIXON.NS', 'ABB.NS', 'BHEL.NS', 'IRFC.NS', 'RVNL.NS', 'PFC.NS', 'RECLTD.NS', 'SJVN.NS', 'HFCL.NS', 'TATACHEM.NS',
    'HDFCLIFE.NS', 'ICICIPRULI.NS', 'ICICIGI.NS', 'SBILIFE.NS', 'HDFCAMC.NS', 'CHOLAFIN.NS', 'MUTHOOTFIN.NS',
    'LTIM.NS', 'PERSISTENT.NS', 'COFORGE.NS', 'NESTLEIND.NS', 'COLPAL.NS', 'GODREJCP.NS', 'MARICO.NS', 'BRITANNIA.NS',
    'HAVELLS.NS', 'BLUEDART.NS', 'DRREDDY.NS', 'AUROPHARMA.NS', 'GLAND.NS', 'LUPIN.NS', 'BIOCON.NS', 'BOSCHLTD.NS',
    'ESCORTS.NS', 'ASHOKLEY.NS', 'TIINDIA.NS', 'SRF.NS', 'DEEPAKNTR.NS', 'PIIND.NS', 'ASTRAL.NS', 'TATVA.NS',
    'ADANIENT.NS', 'VBL.NS', 'SIEMENS.NS', 'KPRMILL.NS', 'AIAENG.NS', 'POLYCAB.NS', 'INDUSTOWER.NS', 'KALYANKJIL.NS'
]

# Technical indicator functions
def compute_rsi(close):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(RSI_PERIOD).mean()
    avg_loss = loss.rolling(RSI_PERIOD).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def compute_macd(close):
    ema_short = close.ewm(span=EMA_SHORT, adjust=False).mean()
    ema_long = close.ewm(span=EMA_LONG, adjust=False).mean()
    macd = ema_short - ema_long
    signal = macd.ewm(span=EMA_SIGNAL, adjust=False).mean()
    macd_diff = macd - signal
    return macd, signal, macd_diff

def get_gann_levels(price):
    base = np.sqrt(price)
    return [round((base + m)**2, 2) for m in [1/8, 1/4, 1/3, 1/2, 1, 2]]

def get_trend(macd, signal, macd_diff, rsi):
    bullish = macd > signal and macd_diff > 0
    bearish = macd < signal and macd_diff < 0

    if bullish and rsi < RSI_OVERBOUGHT:
        return "🟢 Strong Bullish"
    elif bearish and rsi > RSI_OVERSOLD:
        return "🔴 Strong Bearish"
    elif bullish:
        return "🟡 Mild Bullish"
    elif bearish:
        return "🟠 Mild Bearish"
    else:
        return "⚪ Neutral"

# Streamlit UI
st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📊 Stock Trend Dashboard (No Filtering)")

result = []

for symbol in symbols:
    try:
        df = yf.download(symbol, period="60d", interval="1d", progress=False)
        if df.empty or len(df) < 30:
            continue

        df['RSI'] = compute_rsi(df['Close'])
        df['MACD'], df['Signal'], df['MACD_Diff'] = compute_macd(df['Close'])
        latest = df.iloc[-1]

        price = float(latest['Close'])
        rsi = float(latest['RSI'])
        macd = float(latest['MACD'])
        signal = float(latest['Signal'])
        macd_diff = float(latest['MACD_Diff'])
        gann = get_gann_levels(price)
        trend = get_trend(macd, signal, macd_diff, rsi)

        result.append({
            'Symbol': symbol,
            'Price': round(price, 2),
            'RSI': round(rsi, 2),
            'MACD': round(macd, 2),
            'Signal': round(signal, 2),
            'MACD_Diff': round(macd_diff, 2),
            'Gann Levels': ', '.join(map(str, gann)),
            'Trend': trend
        })

    except Exception as e:
        st.warning(f"⚠️ Error with {symbol}: {e}")

if result:
    st.dataframe(pd.DataFrame(result), use_container_width=True)
else:
    st.error("No data available.")
