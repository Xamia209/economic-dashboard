import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_name):
    subprocess.run(
        [sys.executable, script_name],
        cwd=BASE_DIR,
        check=True
    )

if __name__ == "__main__":
    print("📰 Bước 1: Crawl tin tức")
    run_script("collecting_news.py")

    print("🧹 Bước 2: Làm sạch dữ liệu")
    run_script("clean_data.py")

    print("📊 Bước 3: Phân tích sentiment")
    run_script("sentiment_analysis.py")

    print("✅ Hoàn tất cập nhật tin tức")