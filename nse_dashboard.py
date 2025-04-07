import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta

# === SETTINGS ===
st.set_page_config(layout="wide")
st.title("📈 Indian Stock Breakout Dashboard")

tickers = ['INFY.NS', 'TCS.NS', 'WIPRO.NS']
rows = []

# === TECHNICAL THRESHOLDS ===
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

def get_sentiment(rsi, macd_diff):
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

# === DATA PROCESSING ===
for ticker in tickers:
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if df.empty:
            st.warning(f"⚠️ No data for {ticker}")
            continue

        df.dropna(inplace=True)

        close = df['Close']
        df['EMA20'] = ta.trend.ema_indicator(close, window=20).ema_indicator()
        df['RSI'] = ta.momentum.RSIIndicator(close, window=14).rsi()
        macd = ta.trend.MACD(close)
        df['MACD'] = macd.macd()
        df['Signal'] = macd.macd_signal()
        df['MACD_Diff'] = df['MACD'] - df['Signal']

        latest = df.iloc[-1]

        sentiment = get_sentiment(latest['RSI'], latest['MACD_Diff'])
        tgt1, tgt2, tgt3, sl = get_targets_sl(latest['Close'])

        rows.append({
            'Symbol': ticker,
            'Close': round(latest['Close'], 2),
            'EMA20': round(latest['EMA20'], 2),
            'RSI': round(latest['RSI'], 2),
            'MACD': round(latest['MACD'], 2),
            'Signal': round(latest['Signal'], 2),
            'MACD_Diff': round(latest['MACD_Diff'], 2),
            'Sentiment': sentiment,
            'Target 1': tgt1,
            'Target 2': tgt2,
            'Target 3': tgt3,
            'Stop Loss': sl
        })

    except Exception as e:
        st.error(f"⚠️ Error with {ticker}: {e}")

# === DISPLAY TABLE ===
df_final = pd.DataFrame(rows)

if df_final.empty:
    st.warning("No data to display. Please verify stock symbols or network connection.")
else:
    st.dataframe(df_final, use_container_width=True)
