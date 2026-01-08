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

# 🔴 DEBUG: xác nhận code mới
st.warning("🚧 DEBUG: CODE MỚI ĐANG CHẠY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =====================
# SIDEBAR
# =====================
st.sidebar.header("⚙️ Điều khiển")

if st.sidebar.button("🔄 Cập nhật tin tức mới"):
    st.sidebar.info("▶️ Bắt đầu chạy update_news.py")

    try:
        result = subprocess.run(
            [sys.executable, "collecting_news.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=60
        )

        st.sidebar.code(result.stdout)

        if result.returncode != 0:
            st.sidebar.error("❌ Cập nhật thất bại")
            st.sidebar.code(result.stderr)
        else:
            st.sidebar.success("✅ Đã cập nhật xong!")

    except Exception as e:
        st.sidebar.error("❌ Exception khi chạy subprocess")
        st.sidebar.code(str(e))

# =====================
# TIÊU ĐỀ
# =====================
st.title("📊 Dashboard Tin tức Kinh tế")

# =====================
# ĐƯỜNG DẪN FILE
# =====================
NEWS_PATH = os.path.join(BASE_DIR, "sentiment_news.json")
SECTOR_PATH = os.path.join(BASE_DIR, "sector_sentiment_summary.json")

# =====================
# LOAD JSON
# =====================
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
# CHIA CỘT
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

            label = row.get("sentiment_label", "neutral")

            if label == "positive":
                st.success("Tích cực")
            elif label == "negative":
                st.error("Tiêu cực")
            else:
                st.info("Trung tính")

            st.divider()

# =====================
# BÊN PHẢI: PHÂN TÍCH
# =====================
with right_col:
    st.subheader("📈 Phân tích cảm xúc")

    if not df_news.empty and "sentiment_label" in df_news.columns:
        st.bar_chart(df_news["sentiment_label"].value_counts())

    if not df_sector.empty:
        st.subheader("Theo ngành")
        st.dataframe(df_sector)
