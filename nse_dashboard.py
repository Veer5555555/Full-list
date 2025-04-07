import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="📊 Stock Trend Dashboard", layout="wide")
st.title("📈 Indian Stock Trend Dashboard")

RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# All NSE Stock Symbols
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

final_data = []

for symbol in symbols:
    try:
        df = yf.download(symbol, period='3mo', interval='1d', progress=False)
        if df.empty:
            continue
        df.dropna(inplace=True)

        df['EMA20'] = ta.trend.ema_indicator(df['Close'], window=20)
        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        macd_obj = ta.trend.MACD(df['Close'])
        df['MACD'] = macd_obj.macd()
        df['MACD_Signal'] = macd_obj.macd_signal()
        df['MACD_Diff'] = macd_obj.macd_diff()

        latest = df.iloc[-1]
        price = round(float(latest['Close']), 2)
        ema20 = round(float(latest['EMA20']), 2)
        rsi = round(float(latest['RSI']), 2)
        macd = round(float(latest['MACD']), 2)
        signal = round(float(latest['MACD_Signal']), 2)
        macd_diff = round(float(latest['MACD_Diff']), 2)

        bullish = macd > signal and price > ema20
        bearish = macd < signal and price < ema20

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

        # Targets and Stop Loss
        target1 = round(price * 1.02, 2)
        target2 = round(price * 1.04, 2)
        target3 = round(price * 1.06, 2)
        stoploss = round(price * 0.97, 2)

        final_data.append({
            'Symbol': symbol,
            'Price': price,
            'EMA20': ema20,
            'RSI': rsi,
            'MACD': macd,
            'Signal': signal,
            'MACD Diff': macd_diff,
            'Sentiment': sentiment,
            'Target 1': target1,
            'Target 2': target2,
            'Target 3': target3,
            'Stop Loss': stoploss
        })

    except Exception as e:
        st.warning(f"⚠️ Error with {symbol}: {e}")

if final_data:
    df_all = pd.DataFrame(final_data)
    st.dataframe(df_all, use_container_width=True)
else:
    st.error("🚫 No data to display. Check stock symbols or your network connection.")
