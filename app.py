import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Cấu hình giao diện
st.set_page_config(page_title="Gemini Interactive Chart", layout="wide")
st.markdown("<style>div.block-container{padding:1rem;}</style>", unsafe_allow_html=True)

# Lấy dữ liệu (Giữ nguyên phần xử lý dữ liệu cũ)
assets = {"Bitcoin": "BTC-USD", "Vàng (XAUT)": "XAUT-USD"}
selected_name = st.sidebar.selectbox("Tài sản:", list(assets.keys()))
df = yf.download(assets[selected_name], period="1mo", interval="1h")
if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

# Tính chỉ báo
df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
df['RSI14'] = 100 - (100 / (1 + (gain / loss)))

# Vẽ biểu đồ
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.3, 0.7])
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Giá"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], line=dict(color='cyan', width=2), name="EMA200"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['RSI14'], line=dict(color='magenta'), name="RSI"), row=2, col=1)

# Cấu hình TƯƠNG TÁC cho điện thoại
fig.update_layout(
    height=800,
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    dragmode='pan', # Cho phép kéo (di chuyển) bằng 1 ngón
    margin=dict(l=5, r=5, t=10, b=10),
    hovermode='x unified' # Hiển thị thông số khi chạm vào
)

# Bật tính năng Zoom bằng 2 ngón
st.plotly_chart(fig, use_container_width=True, config={
    'scrollZoom': True, # Cho phép zoom bằng 2 ngón (hoặc con lăn chuột)
    'displayModeBar': False, # Ẩn thanh công cụ để màn hình thoáng hơn
})
