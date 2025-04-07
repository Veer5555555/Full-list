import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Stock list (replace with full list you shared)
stock_list = [ 'INFY.NS', 'WIPRO.NS', 'TCS.NS', 'SBIN.NS', 'LICI.NS', 
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

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

def calculate_indicators(df):
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Diff'] = df['MACD'] - df['Signal']
    
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(RSI_PERIOD).mean()
    avg_loss = loss.rolling(RSI_PERIOD).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['GANN'] = df['Close'].rolling(window=30).mean()
    return df

def get_trend(row):
    bullish = (row['Close'] > row['GANN']) and (row['MACD'] > row['Signal']) and (row['MACD_Diff'] > 0)
    bearish = (row['Close'] < row['GANN']) and (row['MACD'] < row['Signal']) and (row['MACD_Diff'] < 0)
    
    if bullish and row['RSI'] < RSI_OVERBOUGHT:
        return "🟢 Strong Bullish"
    elif bearish and row['RSI'] > RSI_OVERSOLD:
        return "🔴 Strong Bearish"
    elif bullish:
        return "🟡 Mild Bullish"
    elif bearish:
        return "🟠 Mild Bearish"
    else:
        return "⚪ Neutral"

st.title("📈 Indian Stock Market Trend Dashboard")

for symbol in stock_list:
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if df.empty or len(df) < 35:
            st.write(f"{symbol}: Not enough data")
            continue
        
        df = calculate_indicators(df)
        latest = df.iloc[-1]
        
        st.subheader(f"{symbol}")
        st.write(f"🔹 Close: {latest['Close']:.2f}")
        st.write(f"🔸 MACD: {latest['MACD']:.2f}, Signal: {latest['Signal']:.2f}, MACD Diff: {latest['MACD_Diff']:.2f}")
        st.write(f"📊 RSI: {latest['RSI']:.2f}")
        st.write(f"🌀 GANN Level: {latest['GANN']:.2f}")
        st.write(f"📌 Trend: **{get_trend(latest)}**")
        
    except Exception as e:
        st.write(f"{symbol}: ⚠️ Error - {str(e)}")
