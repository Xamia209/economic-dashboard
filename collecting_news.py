import requests
import json
import os

def run_daily_task():
    url = "https://gnews.io/api/v4/top-headlines"
    params = {
        "country": "vn",
        "lang": "vi",
        "topic": "business",
        "max": 50,
        "token": "e5ce969339d5238cbb6a72d877fde94e"
    }

    # Gửi yêu cầu đến API
    response = requests.get(url, params=params)

    # Chuyển kết quả nhận được sang dạng Python (dict)
    data = response.json()

    if response.status_code != 200:
        print(f"Lỗi khi gọi API: {response.status_code}")
        print(data)
        return

    # In 5 tin đầu tiên
    for i, article in enumerate(data.get("articles", [])[:5], start=1):
        print(f"{i}. {article['title']}")
        print(article["url"])
        print()

    # Lưu tệp JSON vào cùng thư mục
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "news_data.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ Saved news data to {file_path}")

    html_path = os.path.join(current_dir, "news.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='UTF-8'><title>My News</title></head><body>")
        f.write("<h1>Today's News</h1>")

        for article in data["articles"]:
            title = article["title"]
            url = article["url"]
            source = article["source"]["name"] if article.get("source") else "Unknown source"
            description = article.get("description", "")

            f.write(f"<h2>{title}</h2>")
            f.write(f"<p><strong>Source:</strong> {source}</p>")
            f.write(f"<p>{description}</p>")
            f.write(f"<a href='{url}' target='_blank'>Read more</a><hr>")

        f.write("</body></html>")

    print("✅ News exported to 'news.html' — open it in your browser!")

if __name__ == "__main__":
    run_daily_task()