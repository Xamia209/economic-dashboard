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

# =====================
# SIDEBAR
# =====================
st.sidebar.header("⚙️ Điều khiển")

if st.sidebar.button("🔄 Cập nhật tin tức mới"):
    with st.spinner("Đang cập nhật tin tức..."):
        subprocess.run([sys.executable, "update_news.py"])
    st.success("✅ Đã cập nhật xong!")
    st.rerun()

# =====================
# TIÊU ĐỀ
# =====================
st.title("📊 Dashboard Tin tức Kinh tế")

# =====================
# ĐƯỜNG DẪN FILE
# =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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
df_sector = pd.DataFrame(sector_data).T if isinstance(sector_data, dict) else pd.DataFrame()

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
        # Bộ lọc ngành
        if "sector" in df_news.columns:
            sector_filter = st.selectbox(
                "Lọc theo ngành",
                ["all"] + sorted(df_news["sector"].dropna().unique().tolist())
            )
            if sector_filter != "all":
                df_show = df_news[df_news["sector"] == sector_filter]
            else:
                df_show = df_news
        else:
            df_show = df_news

        for _, row in df_show.iterrows():
            title = row.get("title", "Không có tiêu đề")
            link = row.get("link", "#")
            sector = row.get("sector", "other")
            label = row.get("sentiment_label", "neutral")

            sentiment = row.get("sentiment")
            if isinstance(sentiment, dict):
                score = sentiment.get("compound", 0)
            else:
                score = 0

            st.markdown(f"**{title}**")
            st.caption(f"Ngành: {sector}")

            if link != "#":
                st.markdown(f"[🔗 Đọc bài]({link})")

            if label == "positive":
                st.success(f"Tích cực 😊 ({score:.2f})")
            elif label == "negative":
                st.error(f"Tiêu cực 😟 ({score:.2f})")
            else:
                st.info(f"Trung tính 😐 ({score:.2f})")

            st.divider()

# =====================
# BÊN PHẢI: PHÂN TÍCH
# =====================
with right_col:
    st.subheader("📈 Phân tích cảm xúc")

    # Tổng quan
    if not df_news.empty and "sentiment_label" in df_news.columns:
        st.markdown("**Tổng quan toàn bộ tin**")
        sentiment_count = df_news["sentiment_label"].value_counts()
        st.bar_chart(sentiment_count)

    # Theo ngành (GIỮ NGUYÊN UI, CHỈ THÊM CHECK)
    if not df_sector.empty:
        st.markdown("**Sentiment theo ngành**")
        st.dataframe(df_sector)

        required_cols = ["positive", "neutral", "negative"]
        if all(col in df_sector.columns for col in required_cols):
            chart_data = df_sector[required_cols]
            st.bar_chart(chart_data)
