import json
import os

# Vị trí file JSON gốc
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# KHÔNG dùng thư mục data nữa
input_path = os.path.join(BASE_DIR, "news_data.json")
output_path = os.path.join(BASE_DIR, "clean_data.json")

# 1. Load dữ liệu gốc
with open(input_path, "r", encoding="utf-8") as f:
    raw = json.load(f)

clean_articles = []

# 2. Lọc & chuẩn hóa từng bài
for article in raw.get("articles", []):
    clean_articles.append({
        "title": article.get("title", "").strip(),
        "description": article.get("description", "").strip(),
        "source": article.get("source", {}).get("name", "Unknown"),
        "url": article.get("url", ""),
        "publishedAt": article.get("publishedAt", "")
    })

# 3. Lưu file sạch
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(clean_articles, f, ensure_ascii=False, indent=4)

print("🚀 Done! Data cleaned and saved to clean_data.json")