import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta

st.set_page_config(layout="wide")
st.title("📊 Final Stock Trend Dashboard")

tickers = ['INFY.NS', 'TCS.NS', 'WIPRO.NS']  # Full list can be added later

RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

data_list = []

def calculate_sentiment(rsi, macd_diff):
    if macd_diff > 0 and rsi < RSI_OVERBOUGHT:
        return "🟢 Strong Bullish"
    elif macd_diff < 0 and rsi > RSI_OVERSOLD:
        return "🔴 Strong Bearish"
    elif macd_diff > 0:
        return "🟡 Mild Bullish"
    elif macd_diff < 0:
        return "🟠 Mild Bearish"
    else:
        return "⚪ Neutral"

def get_targets_sl(close):
    return round(close * 1.02, 2), round(close * 1.04, 2), round(close * 1.06, 2), round(close * 0.98, 2)

for symbol in tickers:
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if df.empty or len(df) < 30:
            st.warning(f"⚠️ Not enough data for {symbol}")
            continue

        # Calculate indicators correctly
        ema20 = ta.trend.EMAIndicator(close=df['Close'], window=20)
        df['EMA20'] = ema20.ema_indicator()

        rsi = ta.momentum.RSIIndicator(close=df['Close'], window=14)
        df['RSI'] = rsi.rsi()

        macd = ta.trend.MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Diff'] = macd.macd_diff()

        latest = df.iloc[-1]

        sentiment = calculate_sentiment(latest['RSI'], latest['MACD_Diff'])
        tgt1, tgt2, tgt3, sl = get_targets_sl(latest['Close'])

        data_list.append({
            'Symbol': symbol,
            'Close': round(latest['Close'], 2),
            'EMA20': round(latest['EMA20'], 2),
            'RSI': round(latest['RSI'], 2),
            'MACD': round(latest['MACD'], 2),
            'Signal': round(latest['MACD_Signal'], 2),
            'MACD Diff': round(latest['MACD_Diff'], 2),
            'Sentiment': sentiment,
            'Target 1': tgt1,
            'Target 2': tgt2,
            'Target 3': tgt3,
            'Stop Loss': sl
        })

    except Exception as e:
        st.error(f"⚠️ Error with {symbol}: {e}")

if data_list:
    df_final = pd.DataFrame(data_list)
    st.dataframe(df_final, use_container_width=True)
else:
    st.warning("🚫 No data to display. Check stock symbols or your network connection.")
