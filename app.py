import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Cấu hình tràn viền và bỏ lề thừa
st.set_page_config(page_title="Gemini Pro Trading", layout="wide")
st.markdown("""
    <style>
    .block-container {padding: 1rem 0.5rem 0rem 0.5rem !important;}
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar chọn tài sản
assets = {"BTC": "BTC-USD", "Vàng": "XAUT-USD"}
symbol = st.sidebar.selectbox("Tài sản:", list(assets.keys()))

# 3. Lấy và xử lý dữ liệu (Xử lý Multi-index)
data = yf.download(assets[symbol], period="1mo", interval="1h")
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# 4. Tính toán chỉ báo
data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
delta = data['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
data['RSI14'] = 100 - (100 / (1 + (gain / loss)))
last = data.iloc[-1]

# 5. HIỆN THỊ CHỈ SỐ (Phần này sẽ hiện lại trên biểu đồ)
st.subheader(f"📊 {symbol} Dashboard")
c1, c2, c3 = st.columns(3)
c1.metric("Gía Hiện Tại", f"{last['Close']:,.1f}")
c2.metric("RSI (14)", f"{last['RSI14']:.2f}")
c3.metric("EMA 200", f"{last['EMA200']:,.1f}")

# 6. THIẾT LẬP BIỂU ĐỒ TƯƠNG TÁC
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.3, 0.7])

# Nến và EMA200
fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Giá"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], line=dict(color='#00ffff', width=2), name="EMA200"), row=1, col=1)

# RSI
fig.add_trace(go.Scatter(x=data.index, y=data['RSI14'], line=dict(color='#ff00ff', width=1.5), name="RSI"), row=2, col=1)
fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

# 7. Cấu hình Zoom/Pan mượt mà
fig.update_layout(
    height=700, # Giảm xuống 700 để thấy được cả Metric ở trên
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    dragmode='pan', # 1 ngón để di chuyển
    margin=dict(l=5, r=5, t=10, b=10),
    hovermode='x unified',
    legend=dict(orientation="h", y=1.1, x=1, xanchor="right")
)

# Render biểu đồ với cấu hình Zoom bằng 2 ngón
st.plotly_chart(fig, use_container_width=True, config={
    'scrollZoom': True,      # Bật zoom 2 ngón cho mobile
    'displayModeBar': False, # Ẩn thanh công cụ
    'responsive': True
})
