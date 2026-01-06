import streamlit as st
import pandas as pd
import json
import os

from collecting_news import collect_news
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# =====================
# SETUP
# =====================
st.set_page_config(
    page_title="Economic Dashboard",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NEWS_PATH = os.path.join(BASE_DIR, "sentiment_news.json")
SECTOR_PATH = os.path.join(BASE_DIR, "sector_sentiment_summary.json")

# Ensure NLTK resource (safe for deploy)
nltk.download("vader_lexicon", quiet=True)

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
    Fetch news -> analyze sentiment -> classify sector
    Return: (news_list, sector_summary)
    """
    sia = SentimentIntensityAnalyzer()
    articles = collect_news()

    processed = []
    sector_summary = {}

    for a in articles:
        text = f"{a.get('title','')} {a.get('description','')}"
        sentiment = sia.polarity_scores(text)

        if sentiment["compound"] >= 0.05:
            label = "positive"
        elif sentiment["compound"] <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        title_lower = a.get("title", "").lower()
        sector = "other"

        if "ngân hàng" in title_lower or "bank" in title_lower:
            sector = "banking"
        elif "bất động sản" in title_lower:
            sector = "real_estate"
        elif "chứng khoán" in title_lower or "cổ phiếu" in title_lower:
            sector = "stock"
        elif "lãi suất" in title_lower or "tiền tệ" in title_lower:
            sector = "monetary"

        processed.append({
            "title": a.get("title", ""),
            "description": a.get("description", ""),
            "link": a.get("link", ""),
            "source": a.get("source", ""),
            "publishedAt": a.get("publishedAt", ""),
            "sentiment": sentiment,
            "sentiment_label": label,
            "sector": sector
        })

        sector_summary.setdefault(
            sector, {"positive": 0, "neutral": 0, "negative": 0}
        )
        sector_summary[sector][label] += 1

    return processed, sector_summary


# =====================
# INIT SESSION STATE
# =====================
if "news_data" not in st.session_state:
    st.session_state.news_data = load_json(NEWS_PATH)

if "sector_data" not in st.session_state:
    st.session_state.sector_data = load_json(SECTOR_PATH)

# =====================
# SIDEBAR
# =====================
st.sidebar.header("⚙️ Điều khiển")

if st.sidebar.button("🔄 Cập nhật tin tức mới"):
    with st.spinner("Đang cập nhật tin tức..."):
        news, sector = update_news_pipeline()
        st.session_state.news_data = news
        st.session_state.sector_data = sector

    st.sidebar.success("✅ Đã cập nhật xong!")

# =====================
# DATAFRAME
# =====================
df_news = pd.DataFrame(st.session_state.news_data)
df_sector = (
    pd.DataFrame(st.session_state.sector_data).T
    if isinstance(st.session_state.sector_data, dict)
    else pd.DataFrame()
)

# =====================
# UI
# =====================
st.title("📊 Dashboard Tin tức Kinh tế")
left_col, right_col = st.columns([2, 1])

# -------- LEFT: NEWS --------
with left_col:
    st.subheader("📰 Tin tức kinh tế")

    if df_news.empty:
        st.info("Chưa có dữ liệu tin tức.")
    else:
        sector_filter = st.selectbox(
            "Lọc theo ngành",
            ["all"] + sorted(df_news["sector"].dropna().unique().tolist())
        )

        df_show = (
            df_news if sector_filter == "all"
            else df_news[df_news["sector"] == sector_filter]
        )

        for _, row in df_show.iterrows():
            st.markdown(f"**{row['title']}**")
            st.caption(f"Ngành: {row['sector']}")

            if row["link"]:
                st.markdown(f"[🔗 Đọc bài]({row['link']})")

            if row["sentiment_label"] == "positive":
                st.success("Tích cực")
            elif row["sentiment_label"] == "negative":
                st.error("Tiêu cực")
            else:
                st.info("Trung tính")

            st.divider()

# -------- RIGHT: ANALYTICS --------
with right_col:
    st.subheader("📈 Phân tích cảm xúc")

    if not df_news.empty:
        st.markdown("**Tổng quan toàn bộ tin**")
        st.bar_chart(df_news["sentiment_label"].value_counts())

    if not df_sector.empty:
        st.markdown("**Sentiment theo ngành**")
        st.dataframe(df_sector)
        st.bar_chart(df_sector)
