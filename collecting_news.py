import requests
import os

URL = "https://newsdata.io/api/1/news"
API_KEY = os.getenv("NEWSDATA_API_KEY", "pub_b9cc184c4b25417bace052270458a5d6")

def collect_news():
    params = {
        "country": "vn",
        "language": "vi",
        "category": "business",
        "apikey": API_KEY
    }

    r = requests.get(URL, params=params, timeout=20)
    r.raise_for_status()

    data = r.json()
    if "results" not in data:
        raise RuntimeError(data)

    return data["results"]
