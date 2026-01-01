# update_news.py
import json

def update_news():
    # 👉 chỗ này là code crawl + sentiment của bạn
    news_data = [
        {
            "title": "Sample news",
            "sentiment": "Positive"
        }
    ]

    with open("sentiment_news.json", "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)

    # nếu bạn có sector summary thì ghi tiếp ở đây