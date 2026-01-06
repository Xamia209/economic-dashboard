import requests
import os

URL = "https://newsdata.io/api/1/news"

# ⚠️ KHUYÊN DÙNG ENV, nhưng để bạn test thì giữ cứng cũng OK
API_KEY = os.getenv("NEWSDATA_API_KEY", "pub_b9cc184c4b25417bace052270458a5d6")


def collect_news():
    params = {
        "country": "vn",
        "language": "vi",
        "category": "business",
        "apikey": API_KEY
    }

    try:
        r = requests.get(URL, params=params, timeout=20)

        # ❗ Nếu HTTP != 200 → NÉM LỖI
        r.raise_for_status()

        data = r.json()

        # ❗ API trả sai format
        if "results" not in data:
            raise RuntimeError(f"API trả dữ liệu lạ: {data}")

        return data["results"]

    except Exception as e:
        # ❗ QUAN TRỌNG: KHÔNG print, NÉM LỖI LÊN APP
        raise RuntimeError(f"collect_news FAILED: {e}")
