import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(page_title="Economic Dashboard", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NEWS_PATH = os.path.join(BASE_DIR, "sentiment_news.json")
SECTOR_PATH = os.path.join(BASE_DIR, "sector_sentiment.json")

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

news_data = load_json(NEWS_PATH)
sector_data = load_json(SECTOR_PATH)

st.title("📊 Dashboard Tin tức Kinh tế")

if not news_data:
    st.warning("Chưa có dữ liệu. Hãy chạy collecting_news.py ở local rồi git push.")
    st.stop()

df_news = pd.DataFrame(news_data)
df_sector = pd.DataFrame(sector_data).T

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("📰 Tin tức")

    sector_filter = st.selectbox(
        "Lọc theo ngành",
        ["all"] + sorted(df_news["sector"].unique())
    )

    df_show = (
        df_news[df_news["sector"] == sector_filter]
        if sector_filter != "all"
        else df_news
    )

    for _, row in df_show.iterrows():
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
    st.bar_chart(df_news["sentiment_label"].value_counts())

    st.subheader("📊 Sentiment theo ngành")
    st.bar_chart(df_sector[["positive", "neutral", "negative"]])
