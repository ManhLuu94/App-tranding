import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Cấu hình giao diện và ÉP 1 HÀNG NGANG
st.set_page_config(page_title="Gemini Trading", layout="wide")

st.markdown("""
    <style>
    /* Đẩy nội dung xuống để tránh thanh Share che mất chữ */
    .block-container {
        padding-top: 4rem !important;
        padding-left: 0.1rem !important;
        padding-right: 0.1rem !important;
    }
    
    /* ÉP CỨNG 3 CHỈ SỐ TRÊN 1 HÀNG NGANG KHÔNG CHO TRÀN */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        justify-content: space-between !important;
    }
    [data-testid="stColumn"] {
        width: 32% !important;
        min-width: 0px !important;
        flex: 1 1 0% !important;
    }
    
    /* Thu nhỏ tối đa thẻ Metric để không bị vỡ khung */
    [data-testid="stMetricValue"] { font-size: 0.8rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.55rem !important; }
    div[data-testid="stMetric"] { 
        padding: 2px !important; 
        background-color: #1e2130; 
        border-radius: 4px;
    }

    /* FIX ZOOM: Ép biểu đồ nhận diện thao tác chạm đa điểm */
    .stPlotlyChart { 
        touch-action: pinch-zoom !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar cài đặt
assets = {"BTC": "BTC-USD", "Vàng": "XAUT-USD"}
symbol = st.sidebar.selectbox("Tài sản:", list(assets.keys()))
tf_options = {"1 Giờ": "1h", "4 Giờ": "4h", "1 Ngày": "1d"}
interval = tf_options[st.sidebar.selectbox("Khung:", list(tf_options.keys()))]

# 3. Lấy dữ liệu
data = yf.download(assets[symbol], period="1mo" if interval != "1d" else "1y", interval=interval)
if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)

# 4. Tính toán
data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
delta = data['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
data['RSI14'] = 100 - (100 / (1 + (gain / loss)))
last = data.iloc[-1]

# 5. Hiển thị 3 chỉ số hàng ngang
c1, c2, c3 = st.columns(3)
c1.metric("Giá", f"{last['Close']:,.0f}")
c2.metric("RSI", f"{last['RSI14']:.1f}")
c3.metric("EMA200", f"{last['EMA200']:,.0f}")

# 6. Biểu đồ nến mỏng
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_width=[0.25, 0.75])

fig.add_trace(go.Candlestick(
    x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], 
    increasing_line_color='#26a69a', increasing_fillcolor='#26a69a',
    decreasing_line_color='#ef5350', decreasing_fillcolor='#ef5350',
    line=dict(width=0.7)
), row=1, col=1)

fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], line=dict(color='#00ffff', width=1.2), name="EMA200"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['RSI14'], line=dict(color='#ff00ff', width=1.2), name="RSI"), row=2, col=1)

# 7. Layout & Tương tác
fig.update_layout(
    height=520,
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    dragmode='zoom', # Chế độ mặc định là Zoom để dễ thao tác 2 ngón
    margin=dict(l=5, r=5, t=5, b=5),
    showlegend=False
)
fig.update_xaxes(range=[data.index[-40], data.index[-1]], row=1, col=1)

# 8. Render với config ép Zoom đa điểm
st.plotly_chart(fig, use_container_width=True, config={
    'scrollZoom': True,
    'displayModeBar': False,
    'staticPlot': False,
})
