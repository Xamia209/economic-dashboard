import streamlit as st
import json
import os
import pandas as pd
import subprocess
import sys

# =====================
# CẤU HÌNH TRANG
# =====================
st.set_page_config(
    page_title="Economic Dashboard",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =====================
# SIDEBAR
# =====================
st.sidebar.header("⚙️ Điều khiển")

if st.sidebar.button("🔄 Cập nhật tin tức mới"):
    with st.sidebar.spinner("Đang cập nhật tin tức..."):
        result = subprocess.run(
            [sys.executable, "collecting_news.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            st.sidebar.error("❌ Cập nhật thất bại")
        else:
            st.sidebar.success("✅ Đã cập nhật xong!")

# =====================
# TIÊU ĐỀ
# =====================
st.title("📊 Dashboard Tin tức Kinh tế")

# =====================
# LOAD DATA
# =====================
NEWS_PATH = os.path.join(BASE_DIR, "sentiment_news.json")
SECTOR_PATH = os.path.join(BASE_DIR, "sector_sentiment_summary.json")

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

news_data = load_json(NEWS_PATH)
sector_data = load_json(SECTOR_PATH)

df_news = pd.DataFrame(news_data)
df_sector = (
    pd.DataFrame(sector_data).T
    if isinstance(sector_data, dict)
    else pd.DataFrame()
)

# =====================
# LAYOUT
# =====================
left_col, right_col = st.columns([2, 1])

# =====================
# BÊN TRÁI: TIN TỨC
# =====================
with left_col:
    st.subheader("📰 Tin tức kinh tế")

    if df_news.empty:
        st.info("Chưa có dữ liệu tin tức.")
    else:
        for _, row in df_news.iterrows():
            st.markdown(f"**{row.get('title', '')}**")
            st.caption(f"Ngành: {row.get('sector', 'other')}")
            st.info("Trung tính")
            st.divider()

# =====================
# BÊN PHẢI: BIỂU ĐỒ
# =====================
with right_col:
    st.subheader("📈 Phân tích cảm xúc")

    # Tổng quan sentiment
    if not df_news.empty:
        st.markdown("**Tổng quan sentiment**")
        sentiment_series = (
            df_news["sentiment_label"]
            if "sentiment_label" in df_news.columns
            else pd.Series(["neutral"] * len(df_news))
        )
        st.bar_chart(sentiment_series.value_counts())

    # Theo ngành
    if not df_sector.empty:
        st.markdown("**Theo ngành**")
        st.dataframe(df_sector)
        st.bar_chart(df_sector[["positive", "neutral", "negative"]])
