import requests
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

URL = "https://newsdata.io/api/1/news"
API_KEY = "pub_b9cc184c4b25417bace052270458a5d6"

def run_daily_task():
    all_articles = []
    next_page = None
    max_pages = 2  # ~20 articles

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
        data = response.json()

        if response.status_code != 200:
            print("API_ERROR")
            return

        articles = data.get("results", [])
        all_articles.extend(articles)

        # ASCII ONLY
        print(f"FETCHED {len(articles)}")

        next_page = data.get("nextPage")
        if not next_page:
            break

    # ===== Normalize format =====
    formatted = {
        "articles": [
            {
                "title": a.get("title", ""),
                "description": a.get("description", ""),
                "url": a.get("link", ""),
                "source": {"name": a.get("source_id", "Unknown")},
                "publishedAt": a.get("pubDate", "")
            }
            for a in all_articles
        ]
    }

    # ===== Save JSON =====
    json_path = os.path.join(BASE_DIR, "news_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(formatted, f, ensure_ascii=False, indent=4)

    print(f"SAVED {len(formatted['articles'])}")

    # ===== Export HTML (UTF-8 OK) =====
    html_path = os.path.join(BASE_DIR, "news.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Today's News</title>
    <style>
        body { font-family: Arial; max-width: 900px; margin: auto; }
        h1 { text-align: center; }
        h2 { margin-bottom: 5px; }
        .source { color: gray; font-size: 0.9em; }
        .article { margin-bottom: 30px; }
    </style>
</head>
<body>
    <h1>📰 Tin tức kinh tế hôm nay</h1>
""")

        for a in formatted["articles"]:
            f.write(f"""
    <div class="article">
        <h2>{a['title']}</h2>
        <div class="source">{a['source']['name']} | {a['publishedAt']}</div>
        <p>{a['description']}</p>
        <a href="{a['url']}" target="_blank">Đọc bài</a>
    </div>
    <hr>
""")

        f.write("</body></html>")

    print("HTML_EXPORTED")

if __name__ == "__main__":
    run_daily_task()
