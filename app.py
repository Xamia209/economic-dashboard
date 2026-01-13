import streamlit as st
import subprocess
import sys
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.title("📊 Economic News Dashboard")

if st.button("🔄 Cập nhật tin tức"):
    subprocess.run([sys.executable, "collecting_news.py"], check=True)
    subprocess.run([sys.executable, "sentiment_analysis.py"], check=True)
    st.success("Cập nhật thành công!")

# ===== LOAD DATA =====
with open("sentiment_news.json", "r", encoding="utf-8") as f:
    news = json.load(f)

with open("sector_sentiment_summary.json", "r", encoding="utf-8") as f:
    sector_summary = json.load(f)

st.subheader("📰 Tin tức mới nhất")
for n in news[:10]:
    st.markdown(f"**{n['title']}**  \nSector: `{n['sector']}` | Sentiment: `{n['sentiment_label']}`")
