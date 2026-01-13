import json
import os
import unicodedata
from collections import Counter

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# =====================
# ENSURE NLTK DATA (FIX DEPLOY)
# =====================
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")

# =====================
# PATH
# =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_PATH = os.path.join(BASE_DIR, "clean_data.json")
NEWS_OUTPUT_PATH = os.path.join(BASE_DIR, "sentiment_news.json")
SECTOR_OUTPUT_PATH = os.path.join(BASE_DIR, "sector_sentiment_summary.json")

# =====================
# LOAD DATA
# =====================
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    articles = json.load(f)

# =====================
# INIT SENTIMENT
# =====================
sia = SentimentIntensityAnalyzer()

# =====================
# SECTOR KEYWORDS
# =====================
SECTORS = {
    "banking": ["ngân hàng", "lãi suất", "tín dụng", "nhnn", "vay"],
    "real_estate": ["bất động sản", "địa ốc", "nhà đất", "chung cư"],
    "stock": ["chứng khoán", "cổ phiếu", "vn-index", "vnindex", "hose", "hnx", "upcom"],
    "export": ["xuất khẩu", "kim ngạch", "đơn hàng", "xuất nhập khẩu"],
    "macro": ["kinh tế", "gdp", "lạm phát", "vĩ mô", "tăng trưởng"],
    "industry": ["sản xuất", "công nghiệp", "nhà máy", "khu công nghiệp"],
    "energy": ["năng lượng", "điện", "xăng", "dầu", "nhiên liệu"],
    "retail": ["bán lẻ", "tiêu dùng", "siêu thị", "sức mua"],
    "technology": ["công nghệ", "ai", "phần mềm", "chuyển đổi số"],
    "agriculture": ["nông nghiệp", "lúa gạo", "cà phê", "thủy sản"],
    "policy_law": ["nghị định", "luật", "chính phủ", "quốc hội"]
}

# =====================
# TEXT NORMALIZATION
# =====================
def normalize(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    return text.lower().strip()

def detect_sector(text: str) -> str:
    text = normalize(text)
    scores = {}

    for sector, keywords in SECTORS.items():
        scores[sector] = sum(1 for kw in keywords if normalize(kw) in text)

    best_sector = max(scores, key=scores.get)
    return best_sector if scores[best_sector] > 0 else "other"

# =====================
# ANALYZE ARTICLES
# =====================
results = []

for article in articles:
    title = article.get("title", "")
    description = article.get("description", "")
    text = f"{title} {description}"

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

# =====================
# SAVE sentiment_news.json
# =====================
with open(NEWS_OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

# =====================
# SECTOR SUMMARY
# =====================
summary = {}

for r in results:
    sector = r.get("sector", "other")
    label = r.get("sentiment_label", "neutral")

    summary.setdefault(sector, Counter())
    summary[sector][label] += 1

final_summary = {
    sector: {
        "total": sum(counter.values()),
        "positive": counter.get("positive", 0),
        "neutral": counter.get("neutral", 0),
        "negative": counter.get("negative", 0),
    }
    for sector, counter in summary.items()
}

with open(SECTOR_OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(final_summary, f, ensure_ascii=False, indent=4)
