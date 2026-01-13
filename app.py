import streamlit as st
import json
import os
import pandas as pd
import subprocess
import sys

# =====================
# CONFIG
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
    with st.spinner("Đang cập nhật tin tức..."):

        # 1️⃣ collecting_news.py
        collect = subprocess.run(
            [sys.executable, "collecting_news.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        if collect.returncode != 0:
            st.error("❌ collecting_news.py bị lỗi")
            st.code(collect.stderr)
            st.stop()

        # 2️⃣ sentiment_analysis.py
        sentiment = subprocess.run(
            [sys.executable, "sentiment_analysis.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        if sentiment.returncode != 0:
            st.error("❌ sentiment_analysis.py bị lỗi")
            st.code(sentiment.stderr)
            st.stop()

        st.success("✅ Đã cập nhật xong!")

    st.rerun()

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
# UI
# =====================
st.title("📊 Dashboard Tin tức Kinh tế")

left_col, right_col = st.columns([2, 1])

# =====================
# LEFT: NEWS
# =====================
with left_col:
    st.subheader("📰 Tin tức kinh tế")

    if df_news.empty:
        st.info("Chưa có dữ liệu.")
    else:
        sector_filter = st.selectbox(
            "Lọc theo ngành",
            ["all"] + sorted(df_news["sector"].dropna().unique())
        )

        df_show = (
            df_news if sector_filter == "all"
            else df_news[df_news["sector"] == sector_filter]
        )

        for _, row in df_show.iterrows():
            st.markdown(f"**{row['title']}**")
            st.caption(f"Ngành: {row['sector']}")
            link = row.get("url") or row.get("link") or "#"
            if link != "#":
                st.markdown(f"[🔗 Đọc bài]({link})")

    
            label = row["sentiment_label"]
            score = row["sentiment"]["compound"]

            if label == "positive":
                st.success(f"Tích cực ({score:.2f})")
            elif label == "negative":
                st.error(f"Tiêu cực ({score:.2f})")
            else:
                st.info(f"Trung tính ({score:.2f})")

            st.divider()

# =====================
# RIGHT: ANALYTICS
# =====================
with right_col:
    st.subheader("📈 Phân tích cảm xúc")

    if not df_news.empty:
        st.markdown("**Tổng quan cảm xúc**")
        st.bar_chart(df_news["sentiment_label"].value_counts())

    if not df_sector.empty:
        st.markdown("**Theo ngành**")
        st.bar_chart(df_sector[["positive", "neutral", "negative"]])
