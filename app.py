import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Cấu hình giao diện tràn viền cho điện thoại
st.set_page_config(page_title="Gemini Pro Trading", layout="wide")
st.markdown("<style>div.block-container{padding-top:1rem; padding-bottom:0rem;}</style>", unsafe_allow_html=True)

# 2. Danh sách tài sản
assets = {"Bitcoin": "BTC-USD", "Vàng (XAUT)": "XAUT-USD", "DXY": "DX-Y.NYB"}
selected_name = st.sidebar.selectbox("Chọn tài sản:", list(assets.keys()))
ticker = assets[selected_name]

# 3. Tải dữ liệu và xử lý
df = yf.download(ticker, period="1mo", interval="1h")
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

def add_indicators(df):
    df = df.copy()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI14'] = 100 - (100 / (1 + (gain / loss)))
    return df

df = add_indicators(df)
last = df.iloc[-1]

# 4. Hiển thị thông số nhanh (Metric)
st.write(f"### {selected_name}")
c1, c2, c3 = st.columns(3)
c1.metric("Giá", f"{last['Close']:,.2f}")
c2.metric("RSI14", f"{last['RSI14']:.2f}")
c3.metric("EMA200", f"{last['EMA200']:,.2f}")

# 5. Vẽ biểu đồ - Đây là đoạn hay bị lỗi
# Khởi tạo fig TRƯỚC khi gọi update_layout
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.3, 0.7])

# Nến và EMA200
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Nến"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], line=dict(color='cyan', width=2), name="EMA200"), row=1, col=1)

# RSI
fig.add_trace(go.Scatter(x=df.index, y=df['RSI14'], line=dict(color='magenta', width=1.5), name="RSI"), row=2, col=1)
fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

# 6. Cấu hình hiển thị TO và RÕ trên điện thoại
fig.update_layout(
    height=800,  # Chiều cao vừa vặn màn hình dọc
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    margin=dict(l=5, r=5, t=10, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
