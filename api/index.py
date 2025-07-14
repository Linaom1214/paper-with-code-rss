import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from urllib.parse import urljoin
import re
app = Flask(__name__)
BASE_URL = "https://paperswithcode.com/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
@app.route("/")
def index():
    url = request.args.get("url")
    if not url or not re.match(r'^[\w\-/\.]+$', url):
        return jsonify({"error": "Invalid URL parameter"}), 400
    try:
        response = requests.get(urljoin(BASE_URL, url), headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 400
    soup = BeautifulSoup(response.text, "html.parser")
    # Deduplicate papers
    seen_urls = set()
    papers = []
    
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/paper/" in href and href not in seen_urls and a.text.strip():
            seen_urls.add(href)
            title = a.text.strip()
            if len(title) > 10:  # Filter out likely non-paper links
                papers.append({"title": title, "url": href})
    feed = {
        "version": "https://jsonfeed.org/version/1",
        "title": f"Papers with Code ({url})",
        "home_page_url": urljoin(BASE_URL, url),
        "feed_url": request.url,
        "items": [
            {
                "id": "https://paperswithcode.com" + p["url"],
                "title": p["title"],
                "content_text": p["title"],
                "url": "https://paperswithcode.com" + p["url"],
            }
            for p in papers
        ]
    }
    return jsonify(feed)
