import json
import os
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(BASE_DIR, "clean_data.json")

with open(input_path, "r", encoding="utf-8") as f:
    articles = json.load(f)

sia = SentimentIntensityAnalyzer()
results = []

SECTORS = {
    "banking": ["ngân hàng", "lãi suất", "tín dụng", "vay vốn"],
    "real_estate": ["bất động sản", "nhà đất", "chung cư"],
    "stock": ["chứng khoán", "cổ phiếu", "vn-index"],
    "export": ["xuất khẩu", "xuất nhập khẩu", "đơn hàng"],
}

def detect_sector(text):
    text = text.lower()
    for sector, keywords in SECTORS.items():
        for kw in keywords:
            if kw in text:
                return sector
    return "other"

# ===== PHÂN TÍCH TỪNG BÀI =====
for article in articles:
    text = f"{article.get('title','')} {article.get('description','')}"
    score = sia.polarity_scores(text)

    compound = score["compound"]
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    article["sentiment"] = score
    article["sentiment_label"] = label
    article["sector"] = detect_sector(article.get("title", ""))

    results.append(article)

# ===== LƯU sentiment_news.json =====
output_path = os.path.join(BASE_DIR, "sentiment_news.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print("🔥 Sentiment analysis done!")

# ===== TỔNG HỢP THEO NGÀNH =====
sector_sentiment = {}

for article in results:
    sector = article.get("sector", "other")
    sentiment = article.get("sentiment_label", "neutral")

    sector_sentiment.setdefault(sector, Counter())
    sector_sentiment[sector][sentiment] += 1

summary = {}
for sector, counter in sector_sentiment.items():
    summary[sector] = {
        "total": sum(counter.values()),
        "positive": counter.get("positive", 0),
        "neutral": counter.get("neutral", 0),
        "negative": counter.get("negative", 0),
    }

output_path = os.path.join(BASE_DIR, "sector_sentiment_summary.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=4)

print("✅ Saved sector sentiment summary")