import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. CẤU HÌNH FIX TRÀN & FIX CHE CHỮ
st.set_page_config(page_title="Gemini Trading Pro", layout="wide")

st.markdown("""
    <style>
    /* Đẩy nội dung xuống sâu hơn để không bị thanh Share che */
    .main .block-container {
        padding-top: 4.5rem !important;
        padding-left: 0.1rem !important;
        padding-right: 0.1rem !important;
    }
    
    /* BẢNG CHỈ SỐ TỰ CHẾ: ÉP 1 HÀNG, CHỮ KHÔNG BAO GIỜ TRÀN */
    .price-bar {
        display: flex;
        width: 100%;
        background: #1e2130;
        padding: 5px 0;
        border-radius: 5px;
        margin-bottom: 10px;
        justify-content: space-between;
    }
    .price-item {
        flex: 1;
        text-align: center;
        border-right: 1px solid #333;
    }
    .price-item:last-child { border-right: none; }
    .p-label { font-size: 0.6rem; color: #888; text-transform: uppercase; }
    .p-value { font-size: 0.85rem; font-weight: bold; color: #fff; }

    /* Fix thao tác zoom trên mobile */
    .stPlotlyChart { touch-action: pinch-zoom !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar
st.sidebar.header("Cấu hình")
assets = {"BTC": "BTC-USD", "Vàng": "XAUT-USD"}
symbol = st.sidebar.selectbox("Tài sản", list(assets.keys()))
tf_options = {"1 Giờ": "1h", "4 Giờ": "4h", "1 Ngày": "1d"}
interval = tf_options[st.sidebar.selectbox("Khung", list(tf_options.keys()))]

# 3. Lấy dữ liệu
data = yf.download(assets[symbol], period="1mo" if interval != "1d" else "1y", interval=interval)
if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)

# 4. Tính toán 3 đường EMA & RSI
data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
data['EMA89'] = data['Close'].ewm(span=89, adjust=False).mean()
data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()

delta = data['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
data['RSI14'] = 100 - (100 / (1 + (gain / loss)))
last = data.iloc[-1]

# 5. HIỂN THỊ BẢNG GIÁ (HTML thuần - chống tràn)
st.markdown(f"""
    <div class="price-bar">
        <div class="price-item">
            <div class="p-label">GIÁ BTC</div>
            <div class="p-value">{last['Close']:,.0f}</div>
        </div>
        <div class="price-item">
            <div class="p-label">RSI(14)</div>
            <div class="p-value">{last['RSI14']:.1f}</div>
        </div>
        <div class="price-item">
            <div class="p-label">EMA 200</div>
            <div class="p-value">{last['EMA200']:,.0f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 6. BIỂU ĐỒ NẾN & 3 ĐƯỜNG EMA
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_width=[0.2, 0.8])

# Nến Nhật mỏng
fig.add_trace(go.Candlestick(
    x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], 
    increasing_line_color='#26a69a', increasing_fillcolor='#26a69a',
    decreasing_line_color='#ef5350', decreasing_fillcolor='#ef5350',
    line=dict(width=0.7), name="Giá"
), row=1, col=1)

# Thêm 3 đường EMA theo yêu cầu
fig.add_trace(go.Scatter(x=data.index, y=data['EMA50'], line=dict(color='#00ff00', width=1.2), name="EMA50"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['EMA89'], line=dict(color='#ffff00', width=1.2), name="EMA89"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], line=dict(color='#ff0000', width=1.5), name="EMA200"), row=1, col=1)

# RSI
fig.add_trace(go.Scatter(x=data.index, y=data['RSI14'], line=dict(color='#ff00ff', width=1), name="RSI"), row=2, col=1)

# 7. LAYOUT & ZOOM
fig.update_layout(
    height=580,
    template="plotly_dark",
    xaxis=dict(rangeslider=dict(visible=True, thickness=0.06), type="date"),
    dragmode='pan',
    margin=dict(l=5, r=5, t=5, b=0),
    showlegend=False
)
# Focus vào 40 nến cuối
fig.update_xaxes(range=[data.index[-40], data.index[-1]], row=1, col=1)

# 8. RENDER
st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': False})
