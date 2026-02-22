import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Cấu hình giao diện & Fix tràn màn hình
st.set_page_config(page_title="Gemini Trading", layout="wide")

st.markdown("""
    <style>
    /* Đẩy toàn bộ nội dung xuống dưới thanh Share */
    .main .block-container {
        padding-top: 5rem !important;
        padding-left: 0.1rem !important;
        padding-right: 0.1rem !important;
    }
    
    /* Tự thiết kế hàng chỉ số nằm ngang không bao giờ tràn */
    .metric-container {
        display: flex;
        justify-content: space-around;
        background-color: #1e2130;
        padding: 8px 2px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .metric-box {
        text-align: center;
        flex: 1;
    }
    .metric-label { font-size: 0.65rem; color: #a3a7b7; margin-bottom: 2px; }
    .metric-value { font-size: 0.9rem; font-weight: bold; color: white; }

    /* Ép biểu đồ nhận thao tác zoom */
    .stPlotlyChart { touch-action: pinch-zoom !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar chọn thông số
st.sidebar.header("Cài đặt")
assets = {"BTC": "BTC-USD", "Vàng": "XAUT-USD"}
symbol = st.sidebar.selectbox("Tài sản:", list(assets.keys()))
tf_options = {"1 Giờ": "1h", "4 Giờ": "4h", "1 Ngày": "1d"}
selected_tf = st.sidebar.selectbox("Khung:", list(tf_options.keys()))

# 3. Lấy dữ liệu
data = yf.download(assets[symbol], period="1mo" if tf_options[selected_tf] != "1d" else "1y", interval=tf_options[selected_tf])
if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)

# 4. Tính toán
data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
delta = data['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
data['RSI14'] = 100 - (100 / (1 + (gain / loss)))
last = data.iloc[-1]

# 5. HIỂN THỊ CHỈ SỐ BẰNG HTML (Không bao giờ tràn)
st.markdown(f"""
    <div class="metric-container">
        <div class="metric-box">
            <div class="metric-label">GIÁ</div>
            <div class="metric-value">{last['Close']:,.0f}</div>
        </div>
        <div class="metric-box" style="border-left: 1px solid #333; border-right: 1px solid #333;">
            <div class="metric-label">RSI</div>
            <div class="metric-value">{last['RSI14']:.1f}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">EMA200</div>
            <div class="metric-value">{last['EMA200']:,.0f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 6. Biểu đồ với phương án Zoom kết hợp (Slider + Touch)
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_width=[0.2, 0.8])

# Nến mỏng đồng màu
fig.add_trace(go.Candlestick(
    x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], 
    increasing_line_color='#26a69a', increasing_fillcolor='#26a69a',
    decreasing_line_color='#ef5350', decreasing_fillcolor='#ef5350',
    line=dict(width=0.7)
), row=1, col=1)

fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], line=dict(color='#00
