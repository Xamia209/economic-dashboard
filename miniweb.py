from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_FILE = os.path.join(BASE_DIR, "miniweb.html")
DATA_FILE = os.path.join(BASE_DIR, "sector_sentiment_summary.json")


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Main page
        if self.path == "/" or self.path == "/miniweb.html":
            try:
                with open(HTML_FILE, "r", encoding="utf-8") as f:
                    html = f.read()

                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(
                    f"HTML_ERROR: {str(e)}".encode("utf-8")
                )

        # JSON API
        elif self.path == "/data":
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
                )

            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(
                    f"JSON_ERROR: {str(e)}".encode("utf-8")
                )

        # Other paths
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 - Not Found")


def main():
    # ASCII ONLY logs
    print("MINIWEB_START")
    print("LISTENING http://localhost:7777")

    server = HTTPServer(("localhost", 7777), MyHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
