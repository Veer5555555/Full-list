import pandas as pd
import numpy as np
import yfinance as yf

# Sample symbols for testing — you can replace with full list
symbols = ['INFY.NS', 'TCS.NS', 'WIPRO.NS']

results = []

for symbol in symbols:
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)

        if df.empty:
            raise ValueError("No data returned")

        df.dropna(inplace=True)

        # Calculate EMA
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["EMA100"] = df["Close"].ewm(span=100, adjust=False).mean()

        # Calculate RSI
        delta = df["Close"].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=14).mean()
        avg_loss = pd.Series(loss).rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        df["RSI"] = rsi

        # Calculate MACD
        df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
        df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = df["EMA12"] - df["EMA26"]
        df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
        df["MACD_diff"] = df["MACD"] - df["Signal"]

        # Gann Levels (simplified)
        close_price = df["Close"].iloc[-1]
        gann_ratios = [0.25, 0.5, 0.75, 1.0, 1.25]
        gann_levels = ", ".join([str(round(close_price * r, 2)) for r in gann_ratios])

        results.append({
            "Symbol": symbol,
            "Close": round(close_price, 2),
            "EMA20": round(df["EMA20"].iloc[-1], 2),
            "EMA50": round(df["EMA50"].iloc[-1], 2),
            "EMA100": round(df["EMA100"].iloc[-1], 2),
            "RSI": round(df["RSI"].iloc[-1], 2),
            "MACD": round(df["MACD"].iloc[-1], 2),
            "Signal": round(df["Signal"].iloc[-1], 2),
            "MACD_diff": round(df["MACD_diff"].iloc[-1], 2),
            "Gann Levels": gann_levels
        })

    except Exception as e:
        results.append({"Symbol": symbol, "Error": str(e)})

# Create final DataFrame
df_results = pd_
