import requests
import json
import os
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download("vader_lexicon")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

URL = "https://newsdata.io/api/1/news"
API_KEY = "pub_b9cc184c4b25417bace052270458a5d6"

def collect_news():
    params = {
        "country": "vn",
        "language": "vi",
        "category": "business",
        "apikey": API_KEY
    }

    r = requests.get(URL, params=params, timeout=20)
    r.raise_for_status()
    return r.json()["results"]

def main():
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
            "sector": sector,
            "sentiment_label": label
        })

        sector_summary.setdefault(
            sector, {"positive": 0, "neutral": 0, "negative": 0}
        )
        sector_summary[sector][label] += 1

    with open(os.path.join(BASE_DIR, "sentiment_news.json"), "w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False, indent=2)

    with open(os.path.join(BASE_DIR, "sector_sentiment.json"), "w", encoding="utf-8") as f:
        json.dump(sector_summary, f, ensure_ascii=False, indent=2)

    print("✅ Cập nhật dữ liệu xong")

if __name__ == "__main__":
    main()