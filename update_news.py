import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_PATH = os.path.join(BASE_DIR, "sentiment_news.json")

def update_news():
    # 🔹 Demo data (bạn thay bằng crawl thật sau)
    news_data = [
        {
            "title": "Tin kinh tế mới cập nhật",
            "link": "#",
            "sector": "macro",
            "sentiment_label": "positive",
            "sentiment": {
                "compound": 0.56
            },
            "published_at": datetime.now().isoformat()
        },
        {
            "title": "Thị trường tài chính biến động nhẹ",
            "link": "#",
            "sector": "finance",
            "sentiment_label": "neutral",
            "sentiment": {
                "compound": 0.02
            },
            "published_at": datetime.now().isoformat()
        }
    ]

    with open(NEWS_PATH, "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)

    print("✅ Update news thành công")

if __name__ == "__main__":
    update_news()