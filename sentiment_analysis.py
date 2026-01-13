import json
import os
import unicodedata
from collections import Counter
from nltk.sentiment import SentimentIntensityAnalyzer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_PATH = os.path.join(BASE_DIR, "clean_data.json")
NEWS_OUTPUT_PATH = os.path.join(BASE_DIR, "sentiment_news.json")
SECTOR_OUTPUT_PATH = os.path.join(BASE_DIR, "sector_sentiment_summary.json")

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    articles = json.load(f)

sia = SentimentIntensityAnalyzer()

SECTORS = {
    "banking": ["ngân hàng", "lãi suất", "tín dụng", "nhnn", "vay"],
    "real_estate": ["bất động sản", "địa ốc", "nhà đất", "chung cư"],
    "stock": ["chứng khoán", "cổ phiếu", "vn-index", "vnindex", "hose"],
    "export": ["xuất khẩu", "kim ngạch", "đơn hàng"],
    "macro": ["kinh tế", "gdp", "lạm phát", "vĩ mô"],
    "industry": ["sản xuất", "công nghiệp", "nhà máy"],
    "energy": ["năng lượng", "điện", "xăng", "dầu"],
    "retail": ["bán lẻ", "tiêu dùng", "siêu thị"],
    "technology": ["công nghệ", "ai", "phần mềm"],
    "agriculture": ["nông nghiệp", "lúa gạo", "cà phê"],
    "policy_law": ["nghị định", "luật", "chính phủ"]
}

def normalize(text):
    text = unicodedata.normalize("NFC", text.lower())
    return text

def detect_sector(text):
    text = normalize(text)
    scores = {}

    for sector, keywords in SECTORS.items():
        scores[sector] = sum(1 for kw in keywords if kw in text)

    best_sector = max(scores, key=scores.get)
    return best_sector if scores[best_sector] > 0 else "other"

results = []

for article in articles:
    text = f"{article['title']} {article['description']}"

    sentiment = sia.polarity_scores(text)
    compound = sentiment["compound"]

    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    article["sentiment"] = sentiment
    article["sentiment_label"] = label
    article["sector"] = detect_sector(text)

    results.append(article)

with open(NEWS_OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

summary = {}
for r in results:
    s = r["sector"]
    l = r["sentiment_label"]
    summary.setdefault(s, Counter())
    summary[s][l] += 1

final_summary = {
    s: {
        "total": sum(c.values()),
        "positive": c.get("positive", 0),
        "neutral": c.get("neutral", 0),
        "negative": c.get("negative", 0),
    }
    for s, c in summary.items()
}

with open(SECTOR_OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(final_summary, f, ensure_ascii=False, indent=4)
