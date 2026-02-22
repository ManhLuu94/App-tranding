import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. CẤU HÌNH GIAO DIỆN CỰC GỌN
st.set_page_config(page_title="Gemini Trading", layout="wide")

st.markdown("""
    <style>
    .block-container {padding: 0.5rem !important;}
    /* Thu nhỏ chỉ số và xếp hàng ngang */
    [data-testid="stMetricValue"] { font-size: 0.95rem !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { font-size: 0.65rem !important; }
    div[data-testid="stMetric"] { 
        padding: 2px 5px !important; 
        background-color: #1e2130; 
        border-radius: 4px;
        text-align: center;
    }
    /* Khóa zoom trình duyệt để ưu tiên biểu đồ */
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

# 4. Tính toán chỉ báo
data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
delta = data['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
data['RSI14'] = 100 - (100 / (1 + (gain / loss)))
last = data.iloc[-1]

# 5. HIỂN THỊ 3 CHỈ SỐ TRÊN 1 HÀNG NGANG
c1, c2, c3 = st.columns(3)
c1.metric("Gía", f"{last['Close']:,.1f}")
c2.metric("RSI", f"{last['RSI14']:.1f}")
c3.metric("EMA200", f"{last['EMA200']:,.1f}")

# 6. BIỂU ĐỒ TỐI ƯU NẾN (VIỀN MỎNG, ĐỒNG MÀU)
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_width=[0.2, 0.8])

# Cấu hình nến: viền mỏng và cùng màu thân nến
fig.add_trace(go.Candlestick(
    x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], 
    name="Giá",
    increasing_fillcolor='#26a69a', increasing_line_color='#26a69a', # Xanh đồng nhất
    decreasing_fillcolor='#ef5350', decreasing_line_color='#ef5350', # Đỏ đồng nhất
    line=dict(width=1) # Viền mỏng lại
), row=1, col=1)

# EMA200
fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], line=dict(color='#00ffff', width=1.5), name="EMA200"), row=1, col=1)

# RSI
fig.add_trace(go.Scatter(x=data.index, y=data['RSI14'], line=dict(color='#ff00ff', width=1.2), name="RSI"), row=2, col=1)
fig.add_hline(y=70, line_dash="dot", line_color="rgba(255,0,0,0.5)", row=2, col=1)
fig.add_hline(y=30, line_dash="dot", line_color="rgba(0,255,0,0.5)", row=2, col=1)

# 7. LAYOUT & ZOOM
fig.update_layout(
    height=550,
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    dragmode='pan', # Để mặc định là kéo di chuyển cho mượt
    margin=dict(l=5, r=5, t=10, b=5),
    hovermode='x unified',
    showlegend=False
)

# Tự động tập trung vào 40 nến cuối cùng để nhìn cho rõ
fig.update_xaxes(range=[data.index[-40], data.index[-1]], row=1, col=1)

# 8. Render
st.plotly_chart(fig, use_container_width=True, config={
    'scrollZoom': True,
    'displayModeBar': False,
    'responsive': True
})
