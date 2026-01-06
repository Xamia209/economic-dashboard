import streamlit as st
import pandas as pd
import traceback
from collecting_news import collect_news
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# =====================
# SETUP
# =====================
st.set_page_config(page_title="Economic Dashboard", layout="wide")
nltk.download("vader_lexicon", quiet=True)

# =====================
# SESSION STATE
# =====================
if "news_data" not in st.session_state:
    st.session_state.news_data = []

if "sector_data" not in st.session_state:
    st.session_state.sector_data = {}

if "last_error" not in st.session_state:
    st.session_state.last_error = None

# =====================
# PIPELINE
# =====================
def update_news_pipeline():
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

        sector = "other"
        title = a.get("title", "").lower()
        if "ngân hàng" in title or "bank" in title:
            sector = "banking"
        elif "bất động sản" in title:
            sector = "real_estate"

        processed.append({
            "title": a.get("title", ""),
            "sentiment_label": label,
            "sector": sector
        })

        sector_summary.setdefault(
            sector, {"positive": 0, "neutral": 0, "negative": 0}
        )
        sector_summary[sector][label] += 1

    return processed, sector_summary

# =====================
# UPDATE FORM (🔥 QUAN TRỌNG)
# =====================
with st.sidebar.form("update_form"):
    submitted = st.form_submit_button("🔄 Cập nhật tin tức mới")

if submitted:
    st.session_state.last_error = None
    try:
        news, sector = update_news_pipeline()
        st.session_state.news_data = news
        st.session_state.sector_data = sector
        st.sidebar.success("✅ Update thành công")
    except Exception:
        st.session_state.last_error = traceback.format_exc()

# =====================
# SHOW ERROR (NẾU CÓ)
# =====================
if st.session_state.last_error:
    st.error("❌ Lỗi khi cập nhật tin tức")
    st.code(st.session_state.last_error)
    st.stop()

# =====================
# UI
# =====================
st.title("📊 Dashboard Tin tức Kinh tế")

if not st.session_state.news_data:
    st.info("Chưa có dữ liệu. Bấm cập nhật để lấy tin.")
else:
    df = pd.DataFrame(st.session_state.news_data)
    left, right = st.columns([2, 1])

    with left:
        for _, row in df.iterrows():
            st.markdown(f"**{row['title']}**")
            st.caption(f"Ngành: {row['sector']}")
            if row["sentiment_label"] == "positive":
                st.success("Tích cực")
            elif row["sentiment_label"] == "negative":
                st.error("Tiêu cực")
            else:
                st.info("Trung tính")
            st.divider()

    with right:
        st.bar_chart(df["sentiment_label"].value_counts())
