import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator

st.set_page_config(layout="wide")
st.title("📈 Indian Stock Breakout Dashboard with Targets")

# List of your 100+ stocks
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
        df['EMA20'] = EMAIndicator(df['Close']).ema_indicator()
        df['EMA50'] = EMAIndicator(df['Close'], window=50).ema_indicator()
        df['RSI'] = RSIIndicator(df['Close']).rsi()
        macd = MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()
        df['GANN'] = df['Close'].rolling(window=8).mean()
        df.dropna(inplace=True)
        return df
    except Exception as e:
        st.warning(f"⚠️ Error with {symbol}: {e}")
        return None

def analyze_stock(df, symbol):
    latest = df.iloc[-1]
    price = round(latest['Close'], 2)
    ema20 = round(latest['EMA20'], 2)
    ema50 = round(latest['EMA50'], 2)
    rsi = round(latest['RSI'], 2)
    macd_val = round(latest['MACD'], 2)
    signal = round(latest['Signal'], 2)
    macd_diff = round(latest['MACD_Hist'], 2)
    gann = round(latest['GANN'], 2)

    bullish = (price > ema20) and (macd_val > signal) and (rsi > 50)
    bearish = (price < ema20) and (macd_val < signal) and (rsi < 50)

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

    target1 = round(price * 1.02, 2)
    target2 = round(price * 1.04, 2)
    target3 = round(price * 1.06, 2)
    stop_loss = round(price * 0.97, 2)

    return {
        'Symbol': symbol,
        'Price': price,
        'EMA20': ema20,
        'EMA50': ema50,
        'RSI': rsi,
        'MACD': macd_val,
        'Signal Line': signal,
        'MACD Diff': macd_diff,
        'GANN Level': gann,
        'Sentiment': sentiment,
        'Target 1': target1,
        'Target 2': target2,
        'Target 3': target3,
        'Stop Loss': stop_loss
    }

data = []

for symbol in stock_list:
    df = fetch_data(symbol)
    if df is not None:
        try:
            result = analyze_stock(df, symbol)
            data.append(result)
        except Exception as e:
            st.warning(f"⚠️ Error processing {symbol}: {e}")

if data:
    st.dataframe(pd.DataFrame(data).sort_values(by='Sentiment', ascending=False), use_container_width=True)
else:
    st.error("🚫 No data to display. Please check your internet connection or symbols.")
