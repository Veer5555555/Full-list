import yfinance as yf
import pandas as pd
import streamlit as st
import datetime

# --- Constants ---
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# --- Full stock list ---
stocks = [
    'INFY.NS', 'WIPRO.NS', 'TCS.NS', 'SBIN.NS', 'LICI.NS', 'ADANIPORTS.NS', 'TATAMOTORS.NS',
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
    'ADANIENT.NS', 'VBL.NS', 'SIEMENS.NS', 'KPRMILL.NS', 'AIAENG.NS', 'POLYCAB.NS', 'INDUSTOWER.NS',
    'KALYANKJIL.NS'
]

# --- Functions ---
def calculate_rsi(data, period=RSI_PERIOD):
    delta = data['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_gann_levels(price):
    sqrt_price = price ** 0.5
    return {
        'Gann_Up': round((round(sqrt_price) + 1) ** 2),
        'Gann_Down': round((round(sqrt_price) - 1) ** 2)
    }

def classify_trend(macd, signal, rsi, close, gann_up, gann_down):
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

# --- Streamlit UI ---
st.set_page_config(page_title="📊 Stock Breakout Dashboard", layout="wide")
st.title("📈 Stock Breakout Dashboard with GANN, RSI, MACD")

selected_stocks = st.multiselect("Select stocks to analyze:", stocks, default=stocks[:30])
start_date = datetime.datetime.today() - datetime.timedelta(days=100)
end_date = datetime.datetime.today()

# --- Analysis Loop ---
results = []

for symbol in selected_stocks:
    try:
        df = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if df.empty or len(df) < 30:
            continue

        df['RSI'] = calculate_rsi(df)
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Diff'] = df['MACD'] - df['Signal']

        latest = df.iloc[-1]
        close = float(latest['Close'])
        rsi = float(latest['RSI'])
        macd = float(latest['MACD'])
        signal = float(latest['Signal'])
        macd_diff = float(latest['MACD_Diff'])

        gann = calculate_gann_levels(close)
        trend = classify_trend(macd, signal, rsi, close, gann['Gann_Up'], gann['Gann_Down'])

        results.append({
            'Symbol': symbol,
            'Close': close,
            'RSI': round(rsi, 2),
            'MACD': round(macd, 2),
            'Signal': round(signal, 2),
            'MACD_Diff': round(macd_diff, 2),
            'Gann Up': gann['Gann_Up'],
            'Gann Down': gann['Gann_Down'],
            'Trend': trend
        })

    except Exception as e:
        st.warning(f"⚠️ Error with {symbol}: {e}")

# --- Display ---
if results:
    df_final = pd.DataFrame(results)
    st.dataframe(df_final.sort_values("Trend", ascending=False), use_container_width=True)
else:
    st.info("No stock data available. Try selecting different symbols.")
