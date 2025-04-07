import streamlit as st
import pandas as pd
import yfinance as yf
import ta

# Define list of symbols
symbols = [
    'INFY.NS', 'WIPRO.NS', 'TCS.NS', 'SBIN.NS', 'LICI.NS',
    'ADANIPORTS.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'HAL.NS', 'IRCTC.NS'
]

# Constants for indicators
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

st.set_page_config(layout="wide")
st.title("📈 Indian Stock Trend Dashboard")

all_data = []

for symbol in symbols:
    try:
        df = yf.download(symbol, period='3mo', interval='1d')
        if df.empty:
            st.warning(f"⚠️ No data for {symbol}")
            continue
        
        df.dropna(inplace=True)
        df['EMA20'] = ta.trend.EMAIndicator(close=df['Close'], window=20).ema_indicator()
        df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
        
        macd = ta.trend.MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Diff'] = macd.macd_diff()

        latest = df.iloc[-1]

        bullish = bool((latest['MACD'] > latest['MACD_Signal']) and (latest['Close'] > latest['EMA20']))
        bearish = bool((latest['MACD'] < latest['MACD_Signal']) and (latest['Close'] < latest['EMA20']))
        rsi = latest['RSI']

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

        all_data.append({
            'Symbol': symbol,
            'Price': round(float(latest['Close']), 2),
            'RSI': round(float(rsi), 2),
            'MACD': round(float(latest['MACD']), 2),
            'MACD_Signal': round(float(latest['MACD_Signal']), 2),
            'MACD_Diff': round(float(latest['MACD_Diff']), 2),
            'EMA20': round(float(latest['EMA20']), 2),
            'Sentiment': sentiment
        })

    except Exception as e:
        st.error(f"⚠️ Error with {symbol}: {e}")

if all_data:
    result_df = pd.DataFrame(all_data)
    st.dataframe(result_df)
else:
    st.error("🚫 No data to display. Check stock symbols or your network connection.")
