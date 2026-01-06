import streamlit as st
import pandas as pd
import traceback
from collecting_news import collect_news
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# =====================
# CONFIG
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
def update_pipeline():
    sia = SentimentIntensityAnalyzer()
    articles = collect_news()

    news = []
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

        title = a.get("title", "")
        title_lower = title.lower()

        sector = "other"
        if "ngân hàng" in title_lower or "bank" in title_lower:
            sector = "banking"
        elif "bất động sản" in title_lower:
            sector = "real_estate"

        news.append({
            "title": title,
            "sentiment_label": label,
            "sector": sector
        })

        sector_summary.setdefault(
            sector, {"positive": 0, "neutral": 0, "negative": 0}
        )
        sector_summary[sector][label] += 1

    return news, sector_summary

# =====================
# SIDEBAR – FORM (KHÔNG RERUN)
# =====================
with st.sidebar.form("update_form"):
    submitted = st.form_submit_button("🔄 Cập nhật tin tức mới")

if submitted:
    try:
        news, sector = update_pipeline()
        st.session_state.news_data = news
        st.session_state.sector_data = sector
        st.sidebar.success(f"✅ Lấy được {len(news)} bài")
    except Exception:
        st.session_state.last_error = traceback.format_exc()

# =====================
# HIỆN LỖI (KHÓA MÀN HÌNH)
# =====================
if st.session_state.last_error:
    st.error("❌ LỖI KHI CẬP NHẬT TIN TỨC")
    st.code(st.session_state.last_error)
    st.stop()   # ❗ CỰC QUAN TRỌNG – KHÔNG CHO NÓ BIẾN MẤT

# =====================
# UI
# =====================
st.title("📊 Dashboard Tin tức Kinh tế")

if not st.session_state.news_data:
    st.info("Chưa có dữ liệu. Bấm 'Cập nhật tin tức mới'.")
else:
    df = pd.DataFrame(st.session_state.news_data)
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("📰 Tin tức")
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

    with right_col:
        st.subheader("📈 Tổng quan sentiment")
        st.bar_chart(df["sentiment_label"].value_counts())
