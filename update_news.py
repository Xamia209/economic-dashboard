import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_PATH = os.path.join(BASE_DIR, "sentiment_news.json")

def update_news():
    news_data = [
        {
            "title": "Sample news mới",
            "sentiment": "Positive"
        }
    ]

    with open(NEWS_PATH, "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    update_news()