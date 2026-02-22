import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Cấu hình chữ nhỏ lại và biểu đồ tràn viền
st.set_page_config(page_title="Gemini Pro Trading", layout="wide")
st.markdown("""
    <style>
    .block-container {padding: 0.5rem 0.2rem !important;}
    /* Làm chữ các ô Metric bé lại một nửa */
    [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
    div[data-testid="stMetric"] { padding: 5px !important; }
    /* Cố định chiều cao biểu đồ để không bị cuộn trang khi zoom */
    .stPlotlyChart { touch-action: none; }
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

# 5. Hiển thị thông số GỌN GÀNG (3 cột trên 1 hàng)
c1, c2, c3 = st.columns(3)
c1.metric("Giá", f"{last['Close']:,.1f}")
c2.metric("RSI", f"{last['RSI14']:.1f}")
c3.metric("EMA200", f"{last['EMA200']:,.1f}")

# 6. Biểu đồ chiếm diện tích lớn
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_width=[0.25, 0.75])
fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Nến"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], line=dict(color='#00ffff', width=1.5), name="EMA200"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['RSI14'], line=dict(color='#ff00ff', width=1), name="RSI"), row=2, col=1)

# Cấu hình kéo thả mượt mà cho Mobile
fig.update_layout(
    height=800, # Tăng chiều cao biểu đồ
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    dragmode='pan',
    margin=dict(l=0, r=0, t=10, b=0),
    hovermode='x unified',
    legend=dict(orientation="h", y=1.05, x=1, xanchor="right", font=dict(size=10))
)

# 7. Ép trình duyệt cho phép zoom 2 ngón trong vùng chart
st.plotly_chart(fig, use_container_width=True, config={
    'scrollZoom': True,
    'displayModeBar': False,
    'staticPlot': False,
    'doubleClick': 'reset+autosize'
})
