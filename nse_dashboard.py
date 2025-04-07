import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

# List of stocks
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

# Function to analyze one stock
def analyze_stock(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if df.empty: return None

        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['EMA100'] = df['Close'].ewm(span=100).mean()

        delta = df['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))

        ema12 = df['Close'].ewm(span=12).mean()
        ema26 = df['Close'].ewm(span=26).mean()
        df['MACD'] = ema12 - ema26
        df['Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Diff'] = df['MACD'] - df['Signal']

        df['ATR'] = df[['High','Low','Close']].apply(
            lambda x: max(x['High'] - x['Low'], abs(x['High'] - x['Close']), abs(x['Low'] - x['Close'])), axis=1).rolling(14).mean()

        latest = df.iloc[-1]

        # Sentiment Logic
        close = latest['Close']
        bullish = close > latest['EMA20'] > latest['EMA50'] > latest['EMA100']
        bearish = close < latest['EMA20'] < latest['EMA50'] < latest['EMA100']
        rsi = latest['RSI']
        sentiment = "⚪ Neutral"
        if bullish and rsi < 70:
            sentiment = "🟢 Strong Bullish"
        elif bearish and rsi > 30:
            sentiment = "🔴 Strong Bearish"
        elif bullish:
            sentiment = "🟡 Mild Bullish"
        elif bearish:
            sentiment = "🟠 Mild Bearish"

        atr = latest['ATR']
        return {
            "Symbol": symbol,
            "Price": round(close, 2),
            "RSI": round(rsi, 2),
            "MACD": round(latest['MACD'], 2),
            "MACD Diff": round(latest['MACD_Diff'], 2),
            "Sentiment": sentiment,
            "Target 1": round(close + atr, 2),
            "Target 2": round(close + 2 * atr, 2),
            "Target 3": round(close + 3 * atr, 2),
            "Stop Loss": round(close - atr, 2)
        }
    except Exception as e:
        return {"Symbol": symbol, "Error": str(e)}

# Streamlit layout
st.title("📈 Stock Breakout Dashboard with Targets & Stop Loss")
data = [analyze_stock(sym) for sym in symbols]
df = pd.DataFrame(data)
st.dataframe(df)
