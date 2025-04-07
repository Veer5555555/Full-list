import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator, ADXIndicator
from ta.volatility import BollingerBands
from ta.volume import VolumeWeightedAveragePrice

# Constants
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
ADX_STRONG_TREND = 25

def gann_levels(price):
    """Calculate Gann support/resistance levels with more precise multipliers"""
    multipliers = [1.125, 1.25, 1.333, 1.5, 1.618, 1.75, 2.0, 2.25, 2.5, 3.0]
    levels_up = [round(price * m, 2) for m in multipliers]
    levels_down = [round(price / m, 2) for m in multipliers]
    return sorted(list(set(levels_up + levels_down)))  # Remove duplicates

def is_breakout(hist):
    """Enhanced breakout detection with volume confirmation"""
    if len(hist) < 21:
        return False
    recent_high = hist['High'][-21:-1].max()  # Use High instead of Close
    volume_avg = hist['Volume'][-21:-1].mean()
    return (hist['Close'].iloc[-1] > recent_high * 1.01 and  # 1% above resistance
            hist['Volume'].iloc[-1] > volume_avg * 1.5)     # 50% higher volume

def get_trend_signal(close, rsi, macd_diff, adx):
    """Determine bullish/bearish trend with multiple confirmation"""
    # Bullish conditions
    bullish = (
        (close > close.rolling(20).mean().iloc[-1]) and  # Price above SMA20
        (macd_diff > 0) and                             # MACD above signal
        (rsi > 50) and                                   # RSI neutral/bullish
        (adx > ADX_STRONG_TREND)                         # Strong trend
    )
    
    # Bearish conditions
    bearish = (
        (close < close.rolling(20).mean().iloc[-1]) and  # Price below SMA20
        (macd_diff < 0) and                              # MACD below signal
        (rsi < 50) and                                   # RSI neutral/bearish
        (adx > ADX_STRONG_TREND)                         # Strong trend
    )
    
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

# Streamlit app configuration
st.set_page_config(layout="wide")
st.title("📈 Advanced NSE Stock Dashboard with Technical Signals")

# Load NSE symbols (consider caching this)
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

# Add filters
col1, col2 = st.columns(2)
with col1:
    min_price = st.number_input("Minimum Price", min_value=0, value=100)
with col2:
    max_rsi = st.number_input("Maximum RSI", min_value=0, max_value=100, value=70)

progress = st.progress(0)
dashboard_data = []

for idx, symbol in enumerate(nse_symbols):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='40d', interval='1d')  # Extended period for better indicators
        
        if hist.empty or len(hist) < 30:
            continue

        close = hist['Close']
        high = hist['High']
        low = hist['Low']
        volume = hist['Volume']
        price = close.iloc[-1]
        
        # Skip if price filter not met
        if price < min_price:
            continue

        # Technical indicators
        rsi = RSIIndicator(close=close).rsi().iloc[-1]
        
        # Skip if RSI filter not met
        if rsi > max_rsi:
            continue
            
        macd_obj = MACD(close=close)
        macd_diff = macd_obj.macd_diff().iloc[-1]
        macd_line = macd_obj.macd().iloc[-1]
        signal_line = macd_obj.macd_signal().iloc[-1]
        
        # Additional indicators
        adx = ADXIndicator(high=high, low=low, close=close).adx().iloc[-1]
        vwap = VolumeWeightedAveragePrice(high=high, low=low, close=close, volume=volume).vwap().iloc[-1]
        
        # Bollinger Bands
        bb = BollingerBands(close=close)
        bb_upper = bb.bollinger_hband().iloc[-1]
        bb_lower = bb.bollinger_lband().iloc[-1]
        
        sma_20 = SMAIndicator(close=close, window=20).sma_indicator().iloc[-1]
        ema_20 = EMAIndicator(close=close, window=20).ema_indicator().iloc[-1]
        
        breakout = is_breakout(hist)
        trend_signal = get_trend_signal(close, rsi, macd_diff, adx)
        gann = gann_levels(price)

        dashboard_data.append({
            "Symbol": symbol.replace(".NS", ""),
            "Price": round(price, 2),
            "Trend": trend_signal,
            "RSI": round(rsi, 2),
            "MACD": round(macd_line, 2),
            "Signal": round(signal_line, 2),
            "MACD Diff": round(macd_diff, 2),
            "ADX": round(adx, 20),
            "VWAP": round(vwap, 2),
            "BB Width": round((bb_upper - bb_lower)/price*100, 2),  # % width
            "SMA 20": round(sma_20, 2),
            "EMA 20": round(ema_20, 2),
            "Breakout": "✅" if breakout else "❌",
            "Gann Near": ", ".join(map(str, sorted(gann, key=lambda x: abs(x - price))[:4])
        })

    except Exception as e:
        st.warning(f"⚠️ Error with {symbol}: {e}")
    finally:
        progress.progress((idx + 1) / len(nse_symbols))

# Create DataFrame and display
if dashboard_data:
    df = pd.DataFrame(dashboard_data)
    
    # Apply conditional formatting
    def color_trend(val):
        if "Bullish" in val:
            return 'background-color: lightgreen'
        elif "Bearish" in val:
            return 'background-color: lightcoral'
        return ''
    
    styled_df = df.style.applymap(color_trend, subset=['Trend'])
    
    # Sort by trend strength and breakout potential
    df['sort_score'] = df.apply(lambda x: 
        (10 if "Bullish" in x['Trend'] else -10 if "Bearish" in x['Trend'] else 0) +
        (20 if x['Breakout'] == "✅" else 0) +
        (5 if x['ADX'] > ADX_STRONG_TREND else 0), axis=1)
    
    st.dataframe(
        styled_df.sort_values(by="sort_score", ascending=False)
                .drop(columns=['sort_score']),
        use_container_width=True,
        height=800
    )
else:
    st.warning("No stocks match your filters. Try adjusting your criteria.")
