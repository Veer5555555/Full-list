import yfinance as yf
import pandas as pd
import streamlit as st

# Constants
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
GANN_LEVEL_PERCENT = 0.125  # 12.5% above/below close

# List of NSE symbols
symbols = [ 
    'INFY.NS', 'WIPRO.NS', 'TCS.NS', 'SBIN.NS', 'LICI.NS',
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

# Functions
def calculate_rsi(data, period=RSI_PERIOD):
    delta = data['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data):
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    macd_diff = macd - signal
    return macd, signal, macd_diff

def classify_trend(rsi, macd, signal, close, gann_up, gann_down):
    bullish = macd > signal and close > gann_up
    bearish = macd < signal and close < gann_down
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

# Streamlit app
st.set_page_config(layout="wide")
st.title("📈 Stock Breakout Dashboard with RSI, MACD, Gann & Prediction")

results = []
for symbol in symbols:
    try:
        data = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if data.empty or len(data) < 35:
            continue
        data['RSI'] = calculate_rsi(data)
        data['MACD'], data['Signal'], data['MACD_Diff'] = calculate_macd(data)

        latest = data.iloc[-1]
        close = latest['Close']
        rsi = latest['RSI']
        macd = latest['MACD']
        signal_line = latest['Signal']
        macd_diff = latest['MACD_Diff']
        gann_up = close * (1 + GANN_LEVEL_PERCENT)
        gann_down = close * (1 - GANN_LEVEL_PERCENT)

        prediction = classify_trend(rsi, macd, signal_line, close, gann_up, gann_down)

        results.append({
            "Symbol": symbol,
            "Close": round(close, 2),
            "RSI": round(rsi, 2),
            "MACD": round(macd, 2),
            "Signal": round(signal_line, 2),
            "MACD Diff": round(macd_diff, 2),
            "Gann Up": round(gann_up, 2),
            "Gann Down": round(gann_down, 2),
            "Prediction": prediction
        })

    except Exception as e:
        st.warning(f"⚠️ Error with {symbol}: {e}")

# Display result
if results:
    df = pd.DataFrame(results)
    st.dataframe(df.style.applymap(
        lambda v: 'color: green' if isinstance(v, str) and 'Bullish' in v else 
                  ('color: red' if 'Bearish' in v else None), subset=['Prediction']
    ))
else:
    st.error("No data to display. Please check symbols or connectivity.")

