import requests
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

URL = "https://newsdata.io/api/1/news"
API_KEY = "pub_b9cc184c4b25417bace052270458a5d6"

def run_daily_task():
    print("▶️ START collecting_news")

    all_articles = []
    next_page = None
    max_pages = 2  # ~20 tin

    for i in range(max_pages):
        params = {
            "country": "vn",
            "language": "vi",
            "category": "business",
            "apikey": API_KEY
        }

        if next_page:
            params["page"] = next_page

        response = requests.get(URL, params=params, timeout=20)
        print(f"PAGE {i+1} STATUS:", response.status_code)

        data = response.json()

        if "results" not in data:
            print("❌ API trả dữ liệu lạ:", data)
            return

        articles = data["results"]
        all_articles.extend(articles)

        print("FETCHED:", len(articles))

        next_page = data.get("nextPage")
        if not next_page:
            break

    print("TOTAL ARTICLES:", len(all_articles))

    raw_path = os.path.join(BASE_DIR, "sentiment_news.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    sector_summary = {
        "other": {
            "positive": 0,
            "neutral": len(all_articles),
            "negative": 0
        }
    }

    sector_path = os.path.join(BASE_DIR, "sector_sentiment_summary.json")
    with open(sector_path, "w", encoding="utf-8") as f:
        json.dump(sector_summary, f, ensure_ascii=False, indent=2)

    print("✅ DONE")

if __name__ == "__main__":
    run_daily_task()
