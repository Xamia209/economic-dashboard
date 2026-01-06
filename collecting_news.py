# collecting_news.py
import requests
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

URL = "https://newsdata.io/api/1/news"
API_KEY = "pub_b9cc184c4b25417bace052270458a5d6"


def collect_news(max_pages: int = 2):
    """
    Fetch news from NewsData API
    Return: list[dict]
    """
    all_articles = []
    next_page = None

    for _ in range(max_pages):
        params = {
            "country": "vn",
            "language": "vi",
            "category": "business",
            "apikey": API_KEY
        }

        if next_page:
            params["page"] = next_page

        response = requests.get(URL, params=params, timeout=15)
        if response.status_code != 200:
            raise RuntimeError("API_ERROR")

        data = response.json()
        articles = data.get("results", [])
        all_articles.extend(articles)

        next_page = data.get("nextPage")
        if not next_page:
            break

    # Normalize format
    normalized = [
        {
            "title": a.get("title", ""),
            "description": a.get("description", ""),
            "link": a.get("link", ""),
            "source": a.get("source_id", "Unknown"),
            "publishedAt": a.get("pubDate", "")
        }
        for a in all_articles
    ]

    return normalized


def save_raw_news(articles):
    """Optional: save raw news"""
    path = os.path.join(BASE_DIR, "news_data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
