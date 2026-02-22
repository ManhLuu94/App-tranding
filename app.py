import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Cấu hình giao diện và ÉP TRÌNH DUYỆT ƯU TIÊN ZOOM CHO BIỂU ĐỒ
st.set_page_config(page_title="Gemini Pro Trading", layout="wide")
st.markdown("""
    <style>
    .block-container {padding: 0.5rem 0.2rem !important;}
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
    div[data-testid="stMetric"] { padding: 5px !important; background-color: #1e2130; border-radius: 5px; }
    
    /* ĐOẠN QUAN TRỌNG: Ép trình duyệt không được tự ý zoom trang web để dành quyền cho biểu đồ */
    .stPlotlyChart { 
        touch-action: none !important; 
        -ms-touch-action: none !important;
        user-select: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar chọn thông số
st.sidebar.header("Cài đặt")
assets = {"BTC": "BTC-USD", "Vàng": "XAUT-USD"}
symbol = st.sidebar.selectbox("Tài sản:", list(assets.keys()))
tf_options = {"1 Giờ": "1h", "4 Giờ": "4h", "1 Ngày": "1d"}
selected_tf = st.sidebar.selectbox("Khung thời gian:", list(tf_options.keys()))

# 3. Lấy dữ liệu
data = yf.download(assets[symbol], period="1mo" if tf_options[selected_tf] != "1d" else "1y", interval=tf_options[selected_tf])
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# 4. Tính toán chỉ báo
data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
delta = data['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
data['RSI14'] = 100 - (100 / (1 + (gain / loss)))
last = data.iloc[-1]

# 5. Hiển thị thông số (Metric)
c1, c2, c3 = st.columns(3)
c1.metric("Giá", f"{last['Close']:,.1f}")
c2.metric("RSI", f"{last['RSI14']:.1f}")
c3.metric("EMA200", f"{last['EMA200']:,.1f}")

# 6. Vẽ biểu đồ
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_width=[0.25, 0.75])

fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Nến"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], line=dict(color='#00ffff', width=1.5), name="EMA200"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['RSI14'], line=dict(color='#ff00ff', width=1.5), name="RSI"), row=2, col=1)

# 7. Cấu hình tương tác
fig.update_layout(
    height=550, # Chiều cao vừa vặn cho điện thoại
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    dragmode='pan', # 1 ngón để di chuyển
    margin=dict(l=0, r=0, t=10, b=0),
    hovermode='x unified'
)

# 8. Render biểu đồ với cấu hình scrollZoom cưỡng bức
st.plotly_chart(fig, use_container_width=True, config={
    'scrollZoom': True,      # Zoom 2 ngón
    'displayModeBar': False, # Ẩn thanh công cụ
    'responsive': True,
    'staticPlot': False
})
