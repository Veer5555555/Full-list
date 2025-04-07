import yfinance as yf
import pandas as pd
import streamlit as st
import datetime

# Constants
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Full stock list
stocks = [ 'INFY.NS', 'WIPRO.NS', 'TCS.NS', 'SBIN.NS', 'LICI.NS',
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
    'KPRMILL.NS', 'AIAENG.NS', 'POLYCAB.NS', 'INDUSTOWER.NS', 'KALYANKJIL.NS' ]

# Function to calculate RSI
def calculate_rsi(data, period=RSI_PERIOD):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Gann level calculation
def calculate_gann_levels(price):
    sqrt_price = price ** 0.5
    return {
        'Gann_Up': (round(sqrt_price + 1) ** 2),
        'Gann_Down': (round(sqrt_price - 1) ** 2)
    }

# Trend classification
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

# Streamlit UI
st.title("📈 Stock Breakout Dashboard with GANN, RSI, MACD")
selected_stocks = st.multiselect("Select stocks to analyze:", stocks, default=stocks[:30])  # Load 30 by default
end_date = datetime.datetime.today()
start_date = end_date - datetime.timedelta(days=100)

# Main processing
results = []
for symbol in selected_stocks:
    try:
        df = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if df.empty:
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
        signal_line = float(latest['Signal'])
        macd_diff = float(latest['MACD_Diff'])

        gann = calculate_gann_levels(close)
        gann_up = gann['Gann_Up']
        gann_down = gann['Gann_Down']

        trend = classify_trend(macd, signal_line, rsi, close, gann_up, gann_down)

        results.append({
            'Symbol': symbol,
            'Close': close,
            'RSI': round(rsi, 2),
            'MACD': round(macd, 2),
            'Signal': round(signal_line, 2),
            'MACD_Diff': round(macd_diff, 2),
            'Gann Up': gann_up,
            'Gann Down': gann_down,
            'Trend': trend
        })

    except Exception as e:
        st.warning(f"⚠️ Error with {symbol}: {e}")

# Output
if results:
    df_results = pd.DataFrame(results)
    st.dataframe(df_results.sort_values(by="Trend", ascending=False), use_container_width=True)
else:
    st.info("No valid stock data fetched.")
