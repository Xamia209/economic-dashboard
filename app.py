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
    with st.spinner("Đang cập nhật tin tức..."):
        result = subprocess.run(
            [sys.executable, "update_news.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        if result.returncode != 0:
            st.error("Cập nhật thất bại")
            st.code(result.stderr)
        else:
            st.success("✅ Đã cập nhật xong!")

    st.rerun()

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
        # Lọc ngành
        if "sector" in df_news.columns:
            sector_filter = st.selectbox(
                "Lọc theo ngành",
                ["all"] + sorted(df_news["sector"].dropna().unique().tolist())
            )
            df_show = (
                df_news[df_news["sector"] == sector_filter]
                if sector_filter != "all"
                else df_news
            )
        else:
            df_show = df_news

        for _, row in df_show.iterrows():
            title = row.get("title", "Không có tiêu đề")
            link = row.get("link", "#")
            sector = row.get("sector", "other")
            label = row.get("sentiment_label", "neutral")

            sentiment = row.get("sentiment", {})
            score = sentiment.get("compound", 0) if isinstance(sentiment, dict) else 0

            st.markdown(f"**{title}**")
            st.caption(f"Ngành: {sector}")

            if link != "#":
                st.markdown(f"[🔗 Đọc bài]({link})")

            if label == "positive":
                st.success(f"Tích cực ({score:.2f})")
            elif label == "negative":
                st.error(f"Tiêu cực ({score:.2f})")
            else:
                st.info(f"Trung tính ({score:.2f})")

            st.divider()

# =====================
# BÊN PHẢI: PHÂN TÍCH
# =====================
with right_col:
    st.subheader("📈 Phân tích cảm xúc")

    if not df_news.empty and "sentiment_label" in df_news.columns:
        st.markdown("**Tổng quan toàn bộ tin**")
        sentiment_count = df_news["sentiment_label"].value_counts()
        st.bar_chart(sentiment_count)

    if not df_sector.empty:
        st.markdown("**Sentiment theo ngành**")
        st.dataframe(df_sector)

        required_cols = ["positive", "neutral", "negative"]
        if all(col in df_sector.columns for col in required_cols):
            st.bar_chart(df_sector[required_cols])
