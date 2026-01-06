import requests
import os
import time
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

URL = "https://newsdata.io/api/1/news"
API_KEY = "pub_b9cc184c4b25417bace052270458a5d6"


def collect_news(max_pages: int = 2):
    all_articles = []
    next_page = None

    for _ in range(max_pages):
        params = {
            "country": "vn",
            "language": "vi",
            "category": "business",
            "apikey": API_KEY,

            # 🔥 CACHE BUSTER – QUAN TRỌNG NHẤT
            "_ts": int(time.time()),
            "_rnd": random.randint(1, 1_000_000)
        }

        if next_page:
            params["page"] = next_page

        response = requests.get(URL, params=params, timeout=15)

        if response.status_code != 200:
            raise RuntimeError(f"API ERROR {response.status_code}")

        data = response.json()
        articles = data.get("results", [])
        all_articles.extend(articles)

        next_page = data.get("nextPage")
        if not next_page:
            break

    # Normalize
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
