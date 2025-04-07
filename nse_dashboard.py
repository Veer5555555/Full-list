
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="NSE Live Dashboard", layout="wide")

# Replace with full list
nse_symbols = ['INFY.NS', 'WIPRO.NS', 'TCS.NS', 'SBIN.NS', 'LICI.NS', 'ADANIPORTS.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'HAL.NS', 'IRCTC.NS', 'IOC.NS', 'COALINDIA.NS', 'HINDUNILVR.NS', 'PNB.NS', 'RELIANCE.NS', 'ITC.NS', 'VEDL.NS', 'JSWSTEEL.NS', 'NTPC.NS', 'POWERGRID.NS', 'BPCL.NS', 'ONGC.NS', 'NHPC.NS', 'ADANIGREEN.NS', 'GAIL.NS', 'TECHM.NS', 'HCLTECH.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'SUNPHARMA.NS', 'BAJAJFINSV.NS', 'BAJFINANCE.NS', 'MARUTI.NS', 'EICHERMOT.NS', 'M&M.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'AXISBANK.NS', 'BANKBARODA.NS', 'INDUSINDBK.NS', 'IDFCFIRSTB.NS', 'FEDERALBNK.NS', 'CANBK.NS', 'UNIONBANK.NS', 'NAUKRI.NS', 'PAYTM.NS', 'ZOMATO.NS', 'DELHIVERY.NS', 'TATAPOWER.NS', 'UPL.NS', 'LT.NS', 'SBICARD.NS', 'INDIGO.NS', 'BHARTIARTL.NS', 'IDEA.NS', 'BEL.NS', 'TITAN.NS', 'DMART.NS', 'ASIANPAINT.NS', 'DIXON.NS', 'ABB.NS', 'BHEL.NS', 'IRFC.NS', 'RVNL.NS', 'PFC.NS', 'RECLTD.NS', 'SJVN.NS', 'HFCL.NS', 'TATACHEM.NS']

@st.cache_data(ttl=60)
def get_data(symbols):
    data = []
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d", interval="1m")
            if not hist.empty:
                current_price = hist['Close'][-1]
                previous_close = hist['Close'][0]
                change = current_price - previous_close
                pct_change = (change / previous_close) * 100
                data.append({
                    'Symbol': symbol,
                    'Current Price': round(current_price, 2),
                    'Change': round(change, 2),
                    '% Change': round(pct_change, 2)
                })
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    return pd.DataFrame(data)

st.title("📈 NSE Live Stock Dashboard")

selected_symbols = st.multiselect("Select stocks to display", nse_symbols, default=nse_symbols[:10])

if selected_symbols:
    df = get_data(selected_symbols)
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Please select at least one stock to display.")
