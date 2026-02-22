import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Cấu hình giao diện
st.set_page_config(page_title="Gemini Pro Trading", layout="wide")
st.markdown("""
    <style>
    .block-container {padding: 1rem 0.5rem !important;}
    [data-testid="stMetric"] { background-color: #1e2130; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar: Chọn tài sản và KHUNG THỜI GIAN
st.sidebar.header("Tùy chỉnh")
assets = {"BTC": "BTC-USD", "Vàng": "XAUT-USD"}
symbol = st.sidebar.selectbox("Tài sản:", list(assets.keys()))

# Bổ sung chọn Khung thời gian
tf_options = {"1 Giờ": "1h", "4 Giờ": "4h", "1 Ngày": "1d"}
selected_tf = st.sidebar.selectbox("Khung thời gian:", list(tf_options.keys()))
interval = tf_options[selected_tf]

# 3. Lấy dữ liệu theo khung thời gian đã chọn
period = "1mo" if interval != "1d" else "1y" # Nếu chọn 1d thì lấy 1 năm dữ liệu cho rõ
data = yf.download(assets[symbol], period=period, interval=interval)
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# 4. Tính toán chỉ báo
data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
delta = data['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
data['RSI14'] = 100 - (100 / (1 + (gain / loss)))
last = data.iloc[-1]

# 5. Hiển thị thông số
st.subheader(f"📊 {symbol} - Khung {selected_tf}")
c1, c2, c3 = st.columns(3)
c1.metric("Giá", f"{last['Close']:,.1f}")
c2.metric("RSI", f"{last['RSI14']:.2f}")
c3.metric("EMA200", f"{last['EMA200']:,.1f}")

# 6. Biểu đồ tương tác
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.3, 0.7])
fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Nến"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], line=dict(color='#00ffff', width=2), name="EMA200"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['RSI14'], line=dict(color='#ff00ff'), name="RSI"), row=2, col=1)

# Cấu hình kéo thả (Pan) làm mặc định
fig.update_layout(
    height=750,
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    dragmode='pan', 
    margin=dict(l=5, r=5, t=10, b=10),
    hovermode='x unified'
)

# 7. Kích hoạt Zoom đa điểm (Bóp/Mở 2 ngón tay)
st.plotly_chart(fig, use_container_width=True, config={
    'scrollZoom': True,      # Quan trọng: Cho phép zoom 2 ngón
    'displayModeBar': True,  # Hiện thanh công cụ để fen có thể chọn lại chế độ Zoom nếu muốn
    'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
    'responsive': True
})
