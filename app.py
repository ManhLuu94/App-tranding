import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Cấu hình giao diện cực gọn
st.set_page_config(page_title="Gemini Trading Pro", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 4rem !important; padding-left: 0.1rem !important; padding-right: 0.1rem !important; }
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; width: 100% !important; }
    [data-testid="stColumn"] { width: 33% !important; flex: 1 1 0% !important; }
    [data-testid="stMetricValue"] { font-size: 0.85rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.6rem !important; }
    div[data-testid="stMetric"] { padding: 4px !important; background-color: #1e2130; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Lấy dữ liệu (BTC)
symbol = "BTC-USD"
data = yf.download(symbol, period="1mo", interval="1h")
if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)

# 3. Tính toán chỉ báo
data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
delta = data['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
data['RSI14'] = 100 - (100 / (1 + (gain / loss)))
last = data.iloc[-1]

# 4. Hiển thị 3 chỉ số hàng ngang
c1, c2, c3 = st.columns(3)
c1.metric("Giá", f"{last['Close']:,.0f}")
c2.metric("RSI", f"{last['RSI14']:.1f}")
c3.metric("EMA200", f"{last['EMA200']:,.0f}")

# 5. BIỂU ĐỒ VỚI RANGE SLIDER ĐỂ ZOOM
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.25, 0.75])

# Thêm nến
fig.add_trace(go.Candlestick(
    x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
    increasing_line_color='#26a69a', decreasing_line_color='#ef5350', line=dict(width=0.8)
), row=1, col=1)

# Thêm RSI
fig.add_trace(go.Scatter(x=data.index, y=data['RSI14'], line=dict(color='#ff00ff', width=1)), row=2, col=1)

# CẤU HÌNH RANGE SLIDER (Đây là phương án zoom mới)
fig.update_layout(
    height=600,
    template="plotly_dark",
    xaxis=dict(
        rangeslider=dict(visible=True, thickness=0.08), # Thanh trượt zoom ở dưới cùng
        type="date"
    ),
    dragmode='pan', # 1 ngón để di chuyển vùng nhìn
    margin=dict(l=5, r=5, t=10, b=0),
    showlegend=False
)

# Hiển thị
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
