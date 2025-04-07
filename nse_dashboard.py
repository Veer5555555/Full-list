import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# Full list of stocks
stock_symbols = ['INFY.NS', 'WIPRO.NS', 'TCS.NS', 'SBIN.NS', 'LICI.NS', 'ADANIPORTS.NS', 'TATAMOTORS.NS',
                 'TATASTEEL.NS', 'HAL.NS', 'IRCTC.NS', 'IOC.NS', 'COALINDIA.NS', 'HINDUNILVR.NS', 'PNB.NS',
                 'RELIANCE.NS', 'ITC.NS', 'VEDL.NS', 'JSWSTEEL.NS', 'NTPC.NS', 'POWERGRID.NS', 'BPCL.NS',
                 'ONGC.NS', 'NHPC.NS', 'ADANIGREEN.NS', 'GAIL.NS', 'TECHM.NS', 'HCLTECH.NS', 'CIPLA.NS',
                 'DIVISLAB.NS', 'SUNPHARMA.NS', 'BAJAJFINSV.NS', 'BAJFINANCE.NS', 'MARUTI.NS', 'EICHERMOT.NS',
                 'M&M.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'AXISBANK.NS', 'BANKBARODA.NS', 'INDUSINDBK.NS',
                 'IDFCFIRSTB.NS', 'FEDERALBNK.NS', 'CANBK.NS', 'UNIONBANK.NS', 'NAUKRI.NS', 'PAYTM.NS',
                 'ZOMATO.NS', 'DELHIVERY.NS', 'TATAPOWER.NS', 'UPL.NS', 'LT.NS', 'SBICARD.NS', 'INDIGO.NS',
                 'BHARTIARTL.NS', 'IDEA.NS', 'BEL.NS', 'TITAN.NS', 'DMART.NS', 'ASIANPAINT.NS', 'DIXON.NS',
                 'ABB.NS', 'BHEL.NS', 'IRFC.NS', 'RVNL.NS', 'PFC.NS', 'RECLTD.NS', 'SJVN.NS', 'HFCL.NS',
                 'TATACHEM.NS', 'HDFCLIFE.NS', 'ICICIPRULI.NS', 'ICICIGI.NS', 'SBILIFE.NS', 'HDFCAMC.NS',
                 'CHOLAFIN.NS', 'MUTHOOTFIN.NS', 'LTIM.NS', 'PERSISTENT.NS', 'COFORGE.NS', 'NESTLEIND.NS',
                 'COLPAL.NS', 'GODREJCP.NS', 'MARICO.NS', 'BRITANNIA.NS', 'HAVELLS.NS', 'BLUEDART.NS',
                 'DRREDDY.NS', 'AUROPHARMA.NS', 'GLAND.NS', 'LUPIN.NS', 'BIOCON.NS', 'BOSCHLTD.NS', 'ESCORTS.NS',
                 'ASHOKLEY.NS', 'TIINDIA.NS', 'SRF.NS', 'DEEPAKNTR.NS', 'PIIND.NS', 'ASTRAL.NS', 'TATVA.NS',
                 'ADANIENT.NS', 'VBL.NS', 'SIEMENS.NS', 'KPRMILL.NS', 'AIAENG.NS', 'POLYCAB.NS',
                 'INDUSTOWER.NS', 'KALYANKJIL.NS']

# Indicator calculation
def analyze_stock(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 50:
            return None
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['EMA100'] = df['Close'].ewm(span=100, adjust=False).mean()
        delta = df['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Diff'] = df['MACD'] - df['Signal']
        tr = pd.concat([
            df['High'] - df['Low'],
            abs(df['High'] - df['Close'].shift()),
            abs(df['Low'] - df['Close'].shift())
        ], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(14).mean()
        latest = df.iloc[-1]
        close = latest['Close']
        bullish = close > latest['EMA20'] > latest['EMA50'] > latest['EMA100']
        bearish = close < latest['EMA20'] < latest['EMA50'] < latest['EMA100']
        if bullish and latest['RSI'] < 70:
            sentiment = "🟢 Strong Bullish"
        elif bearish and latest['RSI'] > 30:
            sentiment = "🔴 Strong Bearish"
        elif bullish:
            sentiment = "🟡 Mild Bullish"
        elif bearish:
            sentiment = "🟠 Mild Bearish"
        else:
            sentiment = "⚪ Neutral"
        return {
            "Symbol": symbol,
            "Price": round(close, 2),
            "RSI": round(latest['RSI'], 2),
            "MACD": round(latest['MACD'], 2),
            "MACD_Diff": round(latest['MACD_Diff'], 2),
            "Sentiment": sentiment,
            "Target 1": round(close + latest['ATR'], 2),
            "Target 2": round(close + 2 * latest['ATR'], 2),
            "Target 3": round(close + 3 * latest['ATR'], 2),
            "Stop Loss": round(close - latest['ATR'], 2)
        }
    except:
        return None

# Streamlit app setup
st.set_page_config(layout="wide")
st.title("📊 Indian Stock Dashboard with Technical Indicators")
with st.spinner("Fetching stock data..."):
    results = [analyze_stock(symbol) for symbol in stock_symbols]
    results = [res for res in results if res]
df = pd.DataFrame(results)
st.dataframe(df, use_container_width=True)
