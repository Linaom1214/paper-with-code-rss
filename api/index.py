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
    # Find all paper cards
    for paper_card in soup.find_all("div", class_="paper-card"):
        title_tag = paper_card.find("h1")
        if title_tag:
            title = title_tag.text.strip()
            paper_url = title_tag.find("a")["href"]

            # Extract GitHub link
            github_link_tag = paper_card.find("span", class_="item-github-link")
            github_link = github_link_tag.find("a")["href"] if github_link_tag else None

            # Extract abstract
            abstract_tag = paper_card.find("p", class_="item-strip-abstract")
            abstract = abstract_tag.text.strip() if abstract_tag else ""

            papers.append({
                "title": title,
                "url": urljoin(BASE_URL, paper_url),
                "github": github_link,
                "abstract": abstract
            })

    feed = {
        "version": "https://jsonfeed.org/version/1",
        "title": f"Papers with Code ({url})",
        "home_page_url": urljoin(BASE_URL, url),
        "feed_url": "https://example.org/feed.json",
        "items": [
            {
                "id": "https://paperswithcode.com" + p["url"],
                "title": p["title"],
                "content_text": p["abstract"],
                "url": "https://paperswithcode.com" + p["url"],
                "github": p["github"]
            }
            for p in papers if len(p["title"]) > 10
        ],
        "follow_challenge": {
            "feed_id": "84899448763345920",
            "user_id": "55153944803890176"
        }
    }
    
    return jsonify(feed)

if __name__ == "__main__":
    app.run(debug=True)
