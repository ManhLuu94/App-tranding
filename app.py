import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. CẤU HÌNH SIÊU GỌN - ĐẨY SÁT ĐỈNH TUYỆT ĐỐI
st.set_page_config(page_title="Gemini Trading Pro", layout="wide")

st.markdown("""
    <style>
    /* Ẩn header mặc định và ép sát nội dung lên trên cùng */
    header {visibility: hidden;}
    .main .block-container {
        padding-top: 0.5rem !important; 
        padding-left: 0.1rem !important;
        padding-right: 0.1rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* Bảng giá hàng ngang chống tràn chữ */
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

    /* Fix thao tác zoom trên mobile */
    .stPlotlyChart { touch-action: pinch-zoom !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Lấy dữ liệu (BTC)
data = yf.download("BTC-USD", period="1mo", interval="1h")
if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)

# 3. Tính toán chỉ báo
data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
data['EMA89'] = data['Close'].ewm(span=89, adjust=False).mean()
data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()

# Bollinger Bands
data['MA20'] = data['Close'].rolling(window=20).mean()
data['STD20'] = data['Close'].rolling(window=20).std()
data['UpperBB'] = data['MA20'] + (data['STD20'] * 2)
data['LowerBB'] = data['MA20'] - (data['STD20'] * 2)

# RSI
delta = data['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
data['RSI14'] = 100 - (100 / (1 + (gain / loss)))
last = data.iloc[-1]

# 4. THANH CHỈ SỐ SÁT ĐỈNH (HTML)
st.markdown(f"""
    <div class="price-bar">
        <div class="price-item"><div class="p-label">GIÁ BTC</div><div class="p-value">{last['Close']:,.0f}</div></div>
        <div class="price-item"><div class="p-label">RSI(14)</div><div class="p-value">{last['RSI14']:.1f}</div></div>
        <div class="price-item"><div class="p-label">EMA 200</div><div class="p-value">{last['EMA200']:,.0f}</div></div>
    </div>
    """, unsafe_allow_html=True)

# 5. BIỂU ĐỒ (Phân bổ tỷ lệ để hiện thanh Zoom)
fig = make_subplots(
    rows=2, cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.03, 
    row_width=[0.3, 0.7] # Tăng diện tích cho RSI để hiện rõ 30/70
)

# Bollinger Bands: Xanh nước biển nhạt (LightBlue)
fig.add_trace(go.Scatter(x=data.index, y=data['UpperBB'], line=dict(color='lightblue', width=0.8), name="Upper BB", opacity=0.5), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['LowerBB'], line=dict(color='lightblue', width=0.8), fill='tonexty', fillcolor='rgba(173,216,230,0.1)', name="Lower BB"), row=1, col=1)

# Nến Nhật mỏng
fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], 
                             increasing_line_color='#26a69a', decreasing_line_color='#ef5350', line=dict(width=0.7)), row=1, col=1)

# 3 Đường EMA
fig.add_trace(go.Scatter(x=data.index, y=data['EMA50'], line=dict(color='#00ff00', width=1), name="EMA50"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['EMA89'], line=dict(color='#ffff00', width=1), name="EMA89"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], line=dict(color='#ff0000', width=1.3), name="EMA200"), row=1, col=1)

# RSI (Làm sạch grid, chỉ hiện 30/70)
fig.add_trace(go.Scatter(x=data.index, y=data['RSI14'], line=dict(color='#ff00ff', width=1.2)), row=2, col=1)
fig.add_hline(y=70, line_dash="dot", line_color="red", line_width=1, row=2, col=1)
fig.add_hline(y=30, line_dash="dot", line_color="green", line_width=1, row=2, col=1)

# 6. LAYOUT HIỆN THANH ZOOM (Rangeslider)
fig.update_layout(
    height=600,
    template="plotly_dark",
    xaxis=dict(
        rangeslider=dict(visible=True, thickness=0.12), # Hiện lại thanh zoom dày hơn để dễ kéo
        type="date"
    ),
    dragmode='pan',
    margin=dict(l=2, r=2, t=5, b=5),
    showlegend=False
)

# Cấu hình trục Y cho RSI
fig.update_yaxes(showgrid=False, range=[10, 90], tickvals=[30, 70], row=2, col=1)
# Focus vào vùng nến mới nhất
fig.update_xaxes(range=[data.index[-40], data.index[-1]], row=1, col=1)

# 7. RENDER
st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': False})
