# app.py
import streamlit as st
import json
import os
import pandas as pd

from collecting_news import collect_news

st.set_page_config(
    page_title="Economic Dashboard",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NEWS_PATH = os.path.join(BASE_DIR, "sentiment_news.json")
SECTOR_PATH = os.path.join(BASE_DIR, "sector_sentiment_summary.json")


# =====================
# UTILS
# =====================
def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def update_news_pipeline():
    """
    Full update pipeline:
    - collect news
    - analyze sentiment
    - classify sector
    - save json
    """
    from nltk.sentiment import SentimentIntensityAnalyzer

    sia = SentimentIntensityAnalyzer()
    articles = collect_news()

    processed = []
    sector_summary = {}

    for a in articles:
        text = f"{a['title']} {a['description']}"
        sentiment = sia.polarity_scores(text)

        if sentiment["compound"] >= 0.05:
            label = "positive"
        elif sentiment["compound"] <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        sector = "other"
        title_lower = a["title"].lower()
        if "bank" in title_lower or "ngân hàng" in title_lower:
            sector = "banking"
        elif "bất động sản" in title_lower:
            sector = "real_estate"

        processed.append({
            **a,
            "sentiment": sentiment,
            "sentiment_label": label,
            "sector": sector
        })

        sector_summary.setdefault(sector, {"positive": 0, "neutral": 0, "negative": 0})
        sector_summary[sector][label] += 1

    with open(NEWS_PATH, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

    with open(SECTOR_PATH, "w", encoding="utf-8") as f:
        json.dump(sector_summary, f, ensure_ascii=False, indent=2)


# =====================
# SIDEBAR
# =====================
st.sidebar.header("⚙️ Điều khiển")

if st.sidebar.button("🔄 Cập nhật tin tức mới"):
    try:
        with st.spinner("Đang cập nhật tin tức..."):
            update_news_pipeline()

        st.success("✅ Đã cập nhật xong!")
        st.rerun()

    except Exception as e:
        st.error("❌ Cập nhật thất bại")
        st.exception(e)   # 🔥 DÒNG QUAN TRỌNG NHẤT



# =====================
# LOAD DATA
# =====================
news_data = load_json(NEWS_PATH)
sector_data = load_json(SECTOR_PATH)

df_news = pd.DataFrame(news_data)
df_sector = pd.DataFrame(sector_data).T if isinstance(sector_data, dict) else pd.DataFrame()


# =====================
# UI
# =====================
st.title("📊 Dashboard Tin tức Kinh tế")
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("📰 Tin tức kinh tế")

    if df_news.empty:
        st.info("Chưa có dữ liệu tin tức.")
    else:
        sector_filter = st.selectbox(
            "Lọc theo ngành",
            ["all"] + sorted(df_news["sector"].unique())
        )

        df_show = df_news if sector_filter == "all" else df_news[df_news["sector"] == sector_filter]

        for _, row in df_show.iterrows():
            st.markdown(f"**{row['title']}**")
            st.caption(f"Ngành: {row['sector']}")
            st.markdown(f"[🔗 Đọc bài]({row['link']})")

            if row["sentiment_label"] == "positive":
                st.success("Tích cực")
            elif row["sentiment_label"] == "negative":
                st.error("Tiêu cực")
            else:
                st.info("Trung tính")

            st.divider()

with right_col:
    st.subheader("📈 Phân tích cảm xúc")

    if not df_news.empty:
        st.bar_chart(df_news["sentiment_label"].value_counts())

    if not df_sector.empty:
        st.dataframe(df_sector)
        st.bar_chart(df_sector)
