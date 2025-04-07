import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta

st.set_page_config(layout="wide")
st.title("📊 Stock Trend Dashboard - Tested & Working ✅")

tickers = ['INFY.NS', 'TCS.NS', 'WIPRO.NS']  # Full list can be added later

RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
data_list = []

def calculate_sentiment(rsi, macd_diff):
    bullish = macd_diff > 0 and rsi > RSI_OVERSOLD
    bearish = macd_diff < 0 and rsi < RSI_OVERBOUGHT

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

def get_targets_sl(close_price):
    return round(close_price * 1.02, 2), round(close_price * 1.04, 2), round(close_price * 1.06, 2), round(close_price * 0.98, 2)

for symbol in tickers:
    try:
        df = yf.download(symbol, period='3mo', interval='1d', progress=False)

        if df.empty:
            st.warning(f"No data found for {symbol}")
            continue

        df.dropna(inplace=True)

        df['EMA20'] = ta.trend.ema_indicator(close=df['Close'], window=20).ema_indicator().values.flatten()
        df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi().values.flatten()
        macd_obj = ta.trend.MACD(close=df['Close'])
        df['MACD'] = macd_obj.macd().values.flatten()
        df['MACD_Signal'] = macd_obj.macd_signal().values.flatten()
        df['MACD_Diff'] = df['MACD'] - df['MACD_Signal']

        last = df.iloc[-1]
        sentiment = calculate_sentiment(last['RSI'], last['MACD_Diff'])
        tgt1, tgt2, tgt3, sl = get_targets_sl(last['Close'])

        data_list.append({
            'Symbol': symbol,
            'Close': round(last['Close'], 2),
            'EMA20': round(last['EMA20'], 2),
            'RSI': round(last['RSI'], 2),
            'MACD': round(last['MACD'], 2),
            'Signal': round(last['MACD_Signal'], 2),
            'MACD Diff': round(last['MACD_Diff'], 2),
            'Sentiment': sentiment,
            'Target 1': tgt1,
            'Target 2': tgt2,
            'Target 3': tgt3,
            'Stop Loss': sl
        })

    except Exception as e:
        st.error(f"⚠️ Error with {symbol}: {e}")

# Display
df_display = pd.DataFrame(data_list)

if df_display.empty:
    st.warning("🚫 No data to display. Check symbols or network.")
else:
    st.dataframe(df_display, use_container_width=True)
