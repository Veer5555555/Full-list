import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator

st.set_page_config(layout="wide")
st.title("📈 Indian Stock Breakout Dashboard")

stock_list = [
    'INFY.NS', 'WIPRO.NS', 'TCS.NS', 'SBIN.NS', 'LICI.NS', 'ADANIPORTS.NS', 'TATAMOTORS.NS',
    'TATASTEEL.NS', 'HAL.NS', 'IRCTC.NS', 'IOC.NS', 'COALINDIA.NS', 'HINDUNILVR.NS',
    'PNB.NS', 'RELIANCE.NS', 'ITC.NS', 'VEDL.NS', 'JSWSTEEL.NS', 'NTPC.NS', 'POWERGRID.NS',
    'BPCL.NS', 'ONGC.NS', 'NHPC.NS', 'ADANIGREEN.NS', 'GAIL.NS', 'TECHM.NS', 'HCLTECH.NS',
    'CIPLA.NS', 'DIVISLAB.NS', 'SUNPHARMA.NS', 'BAJAJFINSV.NS', 'BAJFINANCE.NS', 'MARUTI.NS',
    'EICHERMOT.NS', 'M&M.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'AXISBANK.NS', 'BANKBARODA.NS',
    'INDUSINDBK.NS', 'IDFCFIRSTB.NS', 'FEDERALBNK.NS', 'CANBK.NS', 'UNIONBANK.NS',
    'NAUKRI.NS', 'PAYTM.NS', 'ZOMATO.NS', 'DELHIVERY.NS', 'TATAPOWER.NS', 'UPL.NS', 'LT.NS',
    'SBICARD.NS', 'INDIGO.NS', 'BHARTIARTL.NS', 'IDEA.NS', 'BEL.NS', 'TITAN.NS', 'DMART.NS',
    'ASIANPAINT.NS', 'DIXON.NS', 'ABB.NS', 'BHEL.NS', 'IRFC.NS', 'RVNL.NS', 'PFC.NS',
    'RECLTD.NS', 'SJVN.NS', 'HFCL.NS', 'TATACHEM.NS', 'HDFCLIFE.NS', 'ICICIPRULI.NS',
    'ICICIGI.NS', 'SBILIFE.NS', 'HDFCAMC.NS', 'CHOLAFIN.NS', 'MUTHOOTFIN.NS', 'LTIM.NS',
    'PERSISTENT.NS', 'COFORGE.NS', 'NESTLEIND.NS', 'COLPAL.NS', 'GODREJCP.NS', 'MARICO.NS',
    'BRITANNIA.NS', 'HAVELLS.NS', 'BLUEDART.NS', 'DRREDDY.NS', 'AUROPHARMA.NS', 'GLAND.NS',
    'LUPIN.NS', 'BIOCON.NS', 'BOSCHLTD.NS', 'ESCORTS.NS', 'ASHOKLEY.NS', 'TIINDIA.NS',
    'SRF.NS', 'DEEPAKNTR.NS', 'PIIND.NS', 'ASTRAL.NS', 'TATVA.NS', 'ADANIENT.NS', 'VBL.NS',
    'SIEMENS.NS', 'KPRMILL.NS', 'AIAENG.NS', 'POLYCAB.NS', 'INDUSTOWER.NS', 'KALYANKJIL.NS'
]

@st.cache_data(ttl=3600)
def fetch_data(symbol):
    try:
        df = yf.download(symbol, period='6mo', interval='1d', progress=False)
        if df.empty:
            return None
        df['EMA20'] = EMAIndicator(close=df['Close'], window=20).ema_indicator()
        df['EMA50'] = EMAIndicator(close=df['Close'], window=50).ema_indicator()
        df['RSI'] = RSIIndicator(close=df['Close']).rsi()
        macd = MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()
        df['GANN'] = df['Close'].rolling(window=8).mean()
        df.dropna(inplace=True)
        return df
    except:
        return None

def analyze(df, symbol):
    row = df.iloc[-1]
    price = float(row['Close'])
    ema20 = float(row['EMA20'])
    ema50 = float(row['EMA50'])
    rsi = float(row['RSI'])
    macd = float(row['MACD'])
    signal = float(row['Signal'])
    macd_hist = float(row['MACD_Hist'])
    gann = float(row['GANN'])

    bullish = price > ema20 and macd > signal and rsi > 50
    bearish = price < ema20 and macd < signal and rsi < 50

    if bullish and rsi < 70:
        sentiment = "🟢 Strong Bullish"
    elif bearish and rsi > 30:
        sentiment = "🔴 Strong Bearish"
    elif bullish:
        sentiment = "🟡 Mild Bullish"
    elif bearish:
        sentiment = "🟠 Mild Bearish"
    else:
        sentiment = "⚪ Neutral"

    return {
        'Symbol': symbol,
        'Price': round(price, 2),
        'EMA20': round(ema20, 2),
        'EMA50': round(ema50, 2),
        'RSI': round(rsi, 2),
        'MACD': round(macd, 2),
        'Signal': round(signal, 2),
        'MACD Diff': round(macd_hist, 2),
        'GANN Level': round(gann, 2),
        'Sentiment': sentiment,
        'Target 1': round(price * 1.02, 2),
        'Target 2': round(price * 1.04, 2),
        'Target 3': round(price * 1.06, 2),
        'Stop Loss': round(price * 0.97, 2)
    }

results = []

for symbol in stock_list:
    df = fetch_data(symbol)
    if df is not None:
        try:
            result = analyze(df, symbol)
            results.append(result)
        except:
            pass

if results:
    st.dataframe(pd.DataFrame(results), use_container_width=True)
else:
    st.warning("🚫 No data to display. Check your internet connection or stock symbols.")
