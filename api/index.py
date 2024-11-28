import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from urllib.parse import urljoin

app = Flask(__name__)

BASE_URL = "https://paperswithcode.com/"

@app.route("/")
def index():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Invalid URL"}), 400

    try:
        response = requests.get(urljoin(BASE_URL, url), timeout=5)
    except requests.RequestException:
        return jsonify({"error": "Request failed"}), 400

    if response.status_code != 200:
        return jsonify({"error": "Invalid URL"}), 400

    data = response.text
    soup = BeautifulSoup(data, "html.parser")

    papers = []
    for a in soup.find_all("a", href=True):
        if "/paper/" in a["href"]:
            papers.append({"title": a.text.strip(), "url": a["href"]})

    feed = {
        "version": "https://jsonfeed.org/version/1",
        "title": f"Papers with Code ({url})",
        "home_page_url": urljoin(BASE_URL, url),
        "feed_url": "https://example.org/feed.json",
        "items": [
            {
                "id": "https://paperswithcode.com" + p["url"],
                "title": p["title"],
                "content_text": p["title"],
                "url": "https://paperswithcode.com" + p["url"],
            }
            for p in papers if len(p["title"]) > 10
        ],
    }
    return jsonify(feed)
