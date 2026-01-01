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
    "banking": [
        "ngân hàng", "nhnn", "lãi suất", "tín dụng", "vay",
        "lãi điều hành", "thanh khoản", "huy động vốn"
    ],
    "real_estate": [
        "bất động sản", "địa ốc", "nhà đất", "chung cư",
        "dự án", "thị trường nhà", "mua bán nhà"
    ],
    "stock": [
        "chứng khoán", "cổ phiếu", "vn-index", "vnindex",
        "hose", "hnx", "upcom", "thị trường chứng khoán"
    ],
    "export": [
        "xuất khẩu", "xuất nhập khẩu", "đơn hàng",
        "thương mại", "kim ngạch", "fdi", "xuất sang"
    ],
    "macro": [
        "kinh tế", "tăng trưởng", "lạm phát", "gdp",
        "chính sách", "vĩ mô", "tài khóa", "tiền tệ"
    ]
}

def detect_sector(text):
    text = text.lower()
    score = {}

    for sector, keywords in SECTORS.items():
        score[sector] = sum(1 for kw in keywords if kw in text)

    best_sector = max(score, key=score.get)

    if score[best_sector] == 0:
        return "other"

    return best_sector

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