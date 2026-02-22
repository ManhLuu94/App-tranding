import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. CẤU HÌNH SIÊU GỌN - ĐẨY SÁT MÉP ĐỈNH
st.set_page_config(page_title="Gemini Trading Pro", layout="wide")

st.markdown("""
    <style>
    /* Ép sát nội dung lên trên cùng để lấy chỗ cho phần zoom */
    .main .block-container {
        padding-top: 1.5rem !important; 
        padding-left: 0.1rem !important;
        padding-right: 0.1rem !important;
    }
    header {visibility: hidden;} /* Ẩn header mặc định để tăng diện tích */
    
    .price-bar {
        display: flex;
        width: 100%;
        background: #1e2130;
        padding: 4px 0;
        border-radius: 4px;
        margin-bottom: 2px;
    }
    .price-item {
        flex: 1;
        text-align: center;
        border-right: 1px solid #333;
    }
    .price-item:last-child { border-right: none; }
    .p-label { font-size: 0.45rem; color: #888; }
    .p-value { font-size: 0.7rem; font-weight: bold; color: #fff; }

    .stPlotlyChart { touch-action: pinch-zoom !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Lấy dữ liệu
data = yf.download("BTC-USD", period="1mo", interval="1h")
if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)

# 3. Tính toán
data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
data['EMA89'] = data['Close'].ewm(span=89, adjust=False).mean()
data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
data['MA20'] = data['Close'].rolling(window=20).mean()
data['STD20'] = data['Close'].rolling(window=20).std()
data['UpperBB'] = data['MA20'] + (data['STD20'] * 2)
data['LowerBB'] = data['MA20'] - (data['STD20'] * 2)

delta = data['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
data['RSI14'] = 100 - (100 / (1 + (gain / loss)))
last = data.iloc[-1]

# 4. THANH CHỈ SỐ (Sát mép)
st.markdown(f"""
    <div class="price-bar">
        <div class="price-item"><div class="p-label">GIÁ BTC</div><div class="p-value">{last['Close']:,.0f}</div></div>
        <div class="price-item"><div class="p-label">RSI(14)</div><div class="p-value">{last['RSI14']:.1f}</div></div>
        <div class="price-item"><div class="p-label">EMA 200</div><div class="p-value">{last['EMA200']:,.0f}</div></div>
    </div>
    """, unsafe_allow_html=True)

# 5. BIỂU ĐỒ (Phân bổ lại tỷ lệ: Tăng diện tích cho Slider Zoom)
fig = make_subplots(
    rows=3, cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.01, 
    row_width=[0.18, 0.22, 0.60] # Nới rộng tầng dưới cùng cho Zoom
)

# BB: Màu xanh nước biển nhạt
fig.add_trace(go.Scatter(x=data.index, y=data['UpperBB'], line=dict(color='lightblue', width=0.8), name="Upper BB"), row=1, col=1)
fig.add
