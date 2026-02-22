import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. CẤU HÌNH GIAO DIỆN CỰC GỌN
st.set_page_config(page_title="Gemini Trading", layout="wide")

# CSS để ép zoom và fix hiển thị nến
st.markdown("""
    <style>
    .block-container {padding: 0.5rem !important;}
    [data-testid="stMetricValue"] { font-size: 1.0rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
    div[data-testid="stMetric"] { padding: 2px 10px !important; background-color: #1e2130; border-radius: 5px; }
    
    /* ÉP TRÌNH DUYỆT CHO PHÉP ZOOM TRONG BIỂU ĐỒ */
    .stPlotlyChart { 
        touch-action: pinch-zoom pan-x pan-y !important;
    }
    iframe { pointer-events: auto !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar
st.sidebar.header("Cài đặt")
assets = {"BTC": "BTC-USD", "Vàng": "XAUT-USD"}
symbol = st.sidebar.selectbox("Tài sản:", list(assets.keys()))
tf_options = {"1 Giờ": "1h", "4 Giờ": "4h", "1 Ngày": "1d"}
selected_tf = st.sidebar.selectbox("Khung:", list(tf_options.keys()))

# 3. Lấy dữ liệu
data = yf.download(assets[symbol], period="1mo" if tf_options[selected_tf] != "1d" else "1y", interval=tf_options[selected_tf])
if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)

# 4. Chỉ báo
data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
delta = data['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
data['RSI14'] = 100 - (100 / (1 + (gain / loss)))
last = data.iloc[-1]

# 5. Metric (Gọn hơn nữa)
c1, c2, c3 = st.columns(3)
c1.metric("Giá", f"{last['Close']:,.1f}")
c2.metric("RSI", f"{last['RSI14']:.1f}")
c3.metric("EMA200", f"{last['EMA200']:,.1f}")

# 6. BIỂU ĐỒ - TĂNG CƯỜNG HIỂN THỊ TRUNG TÂM
# Chỉnh vertical_spacing cực nhỏ để nến không bị đẩy đi xa
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_width=[0.2, 0.8])

# Nến
fig.add_trace(go.Candlestick(
    x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], 
    name="Nến", increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
), row=1, col=1)

# EMA200
fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], line=dict(color='#00ffff', width=1.5), name="EMA200"), row=1, col=1)

# RSI
fig.add_trace(go.Scatter(x=data.index, y=data['RSI14'], line=dict(color='#ff00ff', width=1), name="RSI"), row=2, col=1)

# 7. CẤU HÌNH ZOOM VÀ HIỂN THỊ
fig.update_layout(
    height=500, # Chiều cao vừa đẹp để không bị trôi
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    dragmode='zoom', # Để mặc định là zoom để fen dễ thao tác hơn
    margin=dict(l=10, r=10, t=10, b=10),
    hovermode='x unified',
    legend=dict(visible=False) # Ẩn chú thích để rộng chỗ
)

# Cố định vùng hiển thị vào các nến cuối cùng
fig.update_xaxes(range=[data.index[-50], data.index[-1]], row=1, col=1)

# 8. Render với Config ép Zoom
st.plotly_chart(fig, use_container_width=True, config={
    'scrollZoom': True,
    'displayModeBar': True, # Hiện thanh công cụ để fen chọn lại chế độ Pan nếu muốn
    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
    'responsive': True
})
