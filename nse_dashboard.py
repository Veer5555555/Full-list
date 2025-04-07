import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator

# Gann levels
def gann_levels(price):
    multipliers = [1.125, 1.25, 1.333, 1.5, 1.666, 1.75, 2.0, 2.25]
    levels_up = [round(price * m, 2) for m in multipliers]
    levels_down = [round(price / m, 2) for m in multipliers]
    return sorted(levels_up + levels_down)

# Breakout condition: Close > 20-day high and Volume > 20-day avg
def is_breakout(hist):
    if len(hist) < 21:
        return False
    recent_high = hist['Close'][-21:-1].max()
    volume_avg = hist['Volume'][-21:-1].mean()
    return hist['Close'].iloc[-1] > recent_high and hist['Volume'].iloc[-1] > volume_avg

# ✅ Full list of NSE symbols
nse_symbols = [
    'INFY.NS', 'WIPRO.NS', 'TCS.NS', 'SBIN.NS', 'LICI.NS', 'ADANIPORTS.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS',
    'HAL.NS', 'IRCTC.NS', 'IOC.NS', 'COALINDIA.NS', 'HINDUNILVR.NS', 'PNB.NS', 'RELIANCE.NS', 'ITC.NS',
    'VEDL.NS', 'JSWSTEEL.NS', 'NTPC.NS', 'POWERGRID.NS', 'BPCL.NS', 'ONGC.NS', 'NHPC.NS', 'ADANIGREEN.NS',
    'GAIL.NS', 'TECHM.NS', 'HCLTECH.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'SUNPHARMA.NS', 'BAJAJFINSV.NS',
    'BAJFINANCE.NS', 'MARUTI.NS', 'EICHERMOT.NS', 'M&M.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'AXISBANK.NS',
    'BANKBARODA.NS', 'INDUSINDBK.NS', 'IDFCFIRSTB.NS', 'FEDERALBNK.NS', 'CANBK.NS', 'UNIONBANK.NS',
    'NAUKRI.NS', 'PAYTM.NS', 'ZOMATO.NS', 'DELHIVERY.NS', 'TATAPOWER.NS', 'UPL.NS', 'LT.NS', 'SBICARD.NS',
    'INDIGO.NS', 'BHARTIARTL.NS', 'IDEA.NS', 'BEL.NS', 'TITAN.NS', 'DMART.NS', 'ASIANPAINT.NS', 'DIXON.NS',
    'ABB.NS', 'BHEL.NS', 'IRFC.NS', 'RVNL.NS', 'PFC.NS', 'RECLTD.NS', 'SJVN.NS', 'HFCL.NS', 'TATACHEM.NS',
    'HDFCLIFE.NS', 'ICICIPRULI.NS', 'ICICIGI.NS', 'SBILIFE.NS', 'HDFCAMC.NS', 'CHOLAFIN.NS', 'MUTHOOTFIN.NS',
    'LTIM.NS', 'PERSISTENT.NS', 'COFORGE.NS', 'NESTLEIND.NS', 'COLPAL.NS', 'GODREJCP.NS', 'MARICO.NS',
    'BRITANNIA.NS', 'HAVELLS.NS', 'BLUEDART.NS', 'DRREDDY.NS', 'AUROPHARMA.NS', 'GLAND.NS', 'LUPIN.NS',
    'BIOCON.NS', 'BOSCHLTD.NS', 'ESCORTS.NS', 'ASHOKLEY.NS', 'TIINDIA.NS', 'SRF.NS', 'DEEPAKNTR.NS',
    'PIIND.NS', 'ASTRAL.NS', 'TATVA.NS', 'ADANIENT.NS', 'VBL.NS', 'SIEMENS.NS', 'VARUNBEV.NS',
    'KPRMILL.NS', 'AIAENG.NS', 'POLYCAB.NS', 'INDUSTOWER.NS'
]

st.set_page_config(layout="wide")
st.title("📈 Live NSE Stock Dashboard with Breakout, Technicals & Gann Levels")

progress = st.progress(0)
dashboard_data = []

for idx, symbol in enumerate(nse_symbols):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='35d', interval='1d')

        if hist.empty or len(hist) < 25:
            continue

        close = hist['Close']
        volume = hist['Volume']
        price = close.iloc[-1]

        # Technical indicators
        rsi = RSIIndicator(close=close).rsi().iloc[-1]
        macd_obj = MACD(close=close)
        macd_diff = macd_obj.macd_diff().iloc[-1]
        macd_line = macd_obj.macd().iloc[-1]
        signal_line = macd_obj.macd_signal().iloc[-1]

        sma_20 = SMAIndicator(close=close, window=20).sma_indicator().iloc[-1]
        ema_20 = EMAIndicator(close=close, window=20).ema_indicator().iloc[-1]

        breakout = is_breakout(hist)
        gann = gann_levels(price)

        dashboard_data.append({
            "Symbol": symbol.replace(".NS", ""),
            "Price": round(price, 2),
            "RSI": round(rsi, 2),
            "MACD": round(macd_line, 2),
            "Signal": round(signal_line, 2),
            "MACD Diff": round(macd_diff, 2),
            "SMA 20": round(sma_20, 2),
            "EMA 20": round(ema_20, 2),
            "Breakout": "✅" if breakout else "❌",
            "Gann Near": ", ".join(map(str, sorted(gann, key=lambda x: abs(x - price))[:4]))
        })

    except Exception as e:
        st.warning(f"⚠️ Error with {symbol}: {e}")
    finally:
        progress.progress((idx + 1) / len(nse_symbols))

df = pd.DataFrame(dashboard_data)
st.dataframe(df.sort_values(by="Breakout", ascending=False), use_container_width=True)
