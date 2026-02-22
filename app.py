import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Cấu hình giao diện
st.set_page_config(page_title="Gemini Trading 2026", layout="wide")
st.title("📊 Cảnh Báo Trading 2026")

# Danh sách tài sản
assets = {"Bitcoin": "BTC-USD", "Vàng (XAUT)": "XAUT-USD", "DXY": "DX-Y.NYB"}
selected_name = st.sidebar.selectbox("Chọn tài sản:", list(assets.keys()))
ticker = assets[selected_name]

# Tải dữ liệu và xử lý lỗi Multi-index
df = yf.download(ticker, period="1mo", interval="1h")
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0) # Sửa lỗi tại đây

def add_indicators(df):
    df = df.copy()
    # EMA
    df['EMA89'] = df['Close'].ewm(span=89, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
    # Bollinger Bands
    df['MA20'] = df['Close'].rolling(window=20).mean()
    std = df['Close'].rolling(window=20).std()
    df['UpperBB'] = df['MA20'] + (std * 2)
    df['LowerBB'] = df['MA20'] - (std * 2)
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI14'] = 100 - (100 / (1 + (gain / loss)))
    return df

df = add_indicators(df)
last = df.iloc[-1]

# Hiển thị chỉ số nhanh
c1, c2, c3 = st.columns(3)
c1.metric("Giá", f"{last['Close']:,.2f}")
c2.metric("RSI14", f"{last['RSI14']:.2f}")
c3.metric("EMA200", f"{last['EMA200']:,.2f}")

# Vẽ biểu đồ
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.3, 0.7])
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Nến"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], line=dict(color='cyan'), name="EMA200"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['RSI14'], line=dict(color='magenta'), name="RSI"), row=2, col=1)

fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
