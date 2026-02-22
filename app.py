import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. CẤU HÌNH GIAO DIỆN & FIX LỖI CHE CHỮ
st.set_page_config(page_title="Gemini Trading", layout="wide")

st.markdown("""
    <style>
    /* Đẩy toàn bộ nội dung xuống để không bị thanh Share che */
    .block-container {
        padding-top: 3.5rem !important; 
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
    }
    
    /* ÉP 3 CHỈ SỐ THÀNH 1 HÀNG NGANG (Dùng Flexbox) */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px !important;
    }
    [data-testid="stColumn"] {
        width: 33% !important;
        flex: 1 1 auto !important;
    }
    
    /* Thu nhỏ chữ Metric tối đa */
    [data-testid="stMetricValue"] { font-size: 0.85rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.6rem !important; }
    div[data-testid="stMetric"] { 
        padding: 5px !important; 
        background-color: #1e2130; 
        border-radius: 4px;
        min-width: 0px !important;
    }
    
    /* Fix Zoom cho Mobile */
    .stPlotlyChart { touch-action: pinch-zoom pan-x pan-y !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar cài đặt
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

# 5. HIỂN THỊ 3 CHỈ SỐ HÀNG NGANG (Đã fix Flexbox ở trên)
col1, col2, col3 = st.columns(3)
col1.metric("Giá", f"{last['Close']:,.0f}")
col2.metric("RSI", f"{last['RSI14']:.1f}")
col3.metric("EMA200", f"{last['EMA200']:,.0f}")

# 6. BIỂU ĐỒ (NẾN MỎNG - ĐỒNG MÀU)
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_width=[0.25, 0.75])

# Nến Nhật mỏng và cùng màu thân nến
fig.add_trace(go.Candlestick(
    x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], 
    name="Giá",
    increasing_fillcolor='#26a69a', increasing_line_color='#26a69a',
    decreasing_fillcolor='#ef5350', decreasing_line_color='#ef5350',
    line=dict(width=0.8) # Làm viền nến mỏng hơn nữa
), row=1, col=1)

fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], line=dict(color='#00ffff', width=1.5), name="EMA200"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['RSI14'], line=dict(color='#ff00ff', width=1.2), name="RSI"), row=2, col=1)

# 7. LAYOUT & ZOOM
fig.update_layout(
    height=580, # Chiều cao tối ưu để không phải cuộn
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    dragmode='pan',
    margin=dict(l=0, r=0, t=10, b=0),
    hovermode='x unified',
    showlegend=False
)
fig.update_xaxes(range=[data.index[-45], data.index[-1]], row=1, col=1)

# 8. Render
st.plotly_chart(fig, use_container_width=True, config={
    'scrollZoom': True,
    'displayModeBar': False,
    'responsive': True
})
