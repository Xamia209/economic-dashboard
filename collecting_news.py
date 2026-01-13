import requests
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

URL = "https://newsdata.io/api/1/news"
API_KEY = "pub_b9cc184c4b25417bace052270458a5d6"

def run_daily_task():
    all_articles = []
    next_page = None
    max_pages = 2  # 20 articles

    for page in range(max_pages):
        params = {
            "country": "vn",
            "language": "vi",
            "category": "business",
            "apikey": API_KEY
        }

        if next_page:
            params["page"] = next_page

        response = requests.get(URL, params=params, timeout=15)
        data = response.json()

        if response.status_code != 200:
            raise RuntimeError(data)

        articles = data.get("results", [])
        all_articles.extend(articles)

        next_page = data.get("nextPage")
        if not next_page:
            break

    # ===== Normalize =====
    clean_articles = []
    for a in all_articles:
        clean_articles.append({
            "title": a.get("title", ""),
            "description": a.get("description", ""),
            "url": a.get("link", ""),
            "source": a.get("source_id", "Unknown"),
            "publishedAt": a.get("pubDate", "")
        })

    # ===== Save =====
    output_path = os.path.join(BASE_DIR, "clean_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(clean_articles, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_daily_task()