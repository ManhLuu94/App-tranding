import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# 1. Cấu hình giao diện DARK MODE
st.set_page_config(page_title="Gemini Trading Pro 2026", layout="wide")
st.markdown("<style> .main {background-color: #0e1117;} </style>", unsafe_allow_html=True)

st.title("🚀 Hệ Thống Phân Tích & Cảnh Báo Trading 2026")

# 2. Danh sách tài sản & Sidebar
assets = {
    "Bitcoin (BTC)": "BTC-USD",
    "DXY (Chỉ số Đô la)": "DX-Y.NYB",
    "Vàng (Gold)": "GC=F",
    "Bạc (Silver)": "SI=F"
}

st.sidebar.header("⚙️ Cấu Hình")
selected_name = st.sidebar.selectbox("Tài sản:", list(assets.keys()))
tf = st.sidebar.selectbox("Khung thời gian:", ["1h", "4h", "1d"], index=1)
ticker = assets[selected_name]

# 3. Hàm tính toán chỉ báo
def add_indicators(df):
    # EMA 89, 200
    df['EMA89'] = df['Close'].ewm(span=89, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    # Bollinger Bands
    df['MA20'] = df['Close'].rolling(window=20).mean()
    std = df['Close'].rolling(window=20).std()
    df['UpperBB'] = df['MA20'] + (std * 2)
    df['LowerBB'] = df['MA20'] - (std * 2)
    
    # RSI 14
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI14'] = 100 - (100 / (1 + (gain / loss)))
    return df

# 4. Tải dữ liệu và xử lý cảnh báo
data = yf.download(ticker, period="1mo", interval=tf)
data = add_indicators(data)
last = data.iloc[-1]

# Logic Cảnh báo
signal = "⚪ ĐANG THEO DÕI"
color = "white"
if last['RSI14'] < 35 and last['Close'] <= last['LowerBB']:
    signal = "🟢 VÙNG MUA (QUÁ BÁN + CHẠM BB DƯỚI)"
    color = "#00ff00"
elif last['RSI14'] > 65 and last['Close'] >= last['UpperBB']:
    signal = "🔴 VÙNG BÁN (QUÁ MUA + CHẠM BB TRÊN)"
    color = "#ff4b4b"

# 5. Hiển thị Dashboard
col1, col2, col3, col4 = st.columns(4)
col1.metric("Giá Hiện Tại", f"${last['Close']:,.2f}")
col2.metric("RSI (14)", f"{last['RSI14']:.2f}")
col3.metric("EMA 200", f"${last['EMA200']:,.2f}")
col4.markdown(f"**Trạng thái:** <span style='color:{color};'>{signal}</span>", unsafe_allow_html=True)

# 6. Vẽ biểu đồ kỹ thuật
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.3, 0.7])

# Nến & Bollinger Bands
fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Giá"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['UpperBB'], line=dict(color='gray', width=1), name="BB Upper"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['LowerBB'], line=dict(color='gray', width=1), fill='tonexty', name="BB Lower"), row=1, col=1)

# EMA 89 & 200
fig.add_trace(go.Scatter(x=data.index, y=data['EMA89'], line=dict(color='yellow', width=2), name="EMA 89 (Xu hướng ngắn)"), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], line=dict(color='cyan', width=2), name="EMA 200 (Hỗ trợ cứng)"), row=1, col=1)

# RSI
fig.add_trace(go.Scatter(x=data.index, y=data['RSI14'], line=dict(color='magenta'), name="RSI"), row=2, col=1)
fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# Ghi chú cho lệnh của bạn
st.sidebar.divider()
st.sidebar.warning(f"""
**💡 Nhắc nhở chiến thuật:**
- Điểm Long chờ: $70.000
- SL của bạn: $60.000
- **Lưu ý:** EMA 200 hiện tại ở ${last['EMA200']:,.0f}. Nếu giá đóng nến dưới đường Cyan này, hãy cẩn thận!
""")