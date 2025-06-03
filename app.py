import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
from datetime import datetime


# Config
st.set_page_config(page_title="Crypto Signal Scanner", layout="wide")

exchange = ccxt.binance()
coins = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT','BTTC/USDT','PEPE/USDT','SHIB/USDT','BONK/USDT','XEC/USDT']
timeframe = '1h'
limit = 100

# Indicator logic
def analyze(df):
    df['ema_50'] = ta.ema(df['close'], length=50)
    df['rsi'] = ta.rsi(df['close'], length=14)
    macd = ta.macd(df['close'])
    df['macd'] = macd['MACD_12_26_9']
    df['signal'] = macd['MACDs_12_26_9']

    last = df.iloc[-1]

    if last['close'] > last['ema_50'] and last['rsi'] < 70 and last['macd'] > last['signal']:
        return 'LONG'
    elif last['close'] < last['ema_50'] and last['rsi'] > 30 and last['macd'] < last['signal']:
        return 'SHORT'
    else:
        return 'NO TRADE'

# Fetch data
@st.cache_data(ttl=300)
def fetch_data(symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# UI
st.title("📈 Live Crypto Signal Dashboard")
st.caption("Using EMA, RSI, and MACD indicators on 5-minute timeframe.")

col1, col2 = st.columns(2)

results = []

for i, coin in enumerate(coins):
    try:
        df = fetch_data(coin)
        signal = analyze(df)
        results.append((coin, signal))

        color = "green" if signal == "LONG" else "red" if signal == "SHORT" else "gray"
        container = col1 if i % 2 == 0 else col2
        with container:
            st.metric(label=coin, value=signal, delta_color="inverse")
            st.markdown(f"<span style='color:{color}; font-size:18px'>{signal}</span>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error fetching {coin}: {e}")

st.markdown("🔄 Auto-refreshes every 5 minutes.")
st.caption(f"Last update: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
