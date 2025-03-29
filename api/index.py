import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from urllib.parse import urljoin

app = Flask(__name__)

BASE_URL = "https://paperswithcode.com/"
ARXIV_BASE_URL = "https://arxiv.org/html/"
PDF_PREVIEW_BASE_URL = "https://arxiv.org/pdf/"

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
            
            # Get the full URL for the paper (assuming it is an arXiv link)
            full_paper_url = urljoin(ARXIV_BASE_URL, paper_url)

            # Fetch the abstract from Papers with Code
            abstract = fetch_abstract(paper_card)

            # Fetch images from the arXiv PDF HTML preview
            images = fetch_images_from_arxiv_html(full_paper_url)

            papers.append({
                "title": title,
                "url": full_paper_url,
                "github": github_link,
                "abstract": abstract,
                "images": images
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
                "github": p["github"],
                "images": p["images"]
            }
            for p in papers if len(p["title"]) > 10
        ],
        "follow_challenge": {
            "feed_id": "84899448763345920",
            "user_id": "55153944803890176"
        }
    }

    return jsonify(feed)

def fetch_abstract(paper_url):
    try:
        response = requests.get(paper_url, timeout=5)
        if response.status_code == 200:
            data = response.text
            soup = BeautifulSoup(data, "html.parser")
            # Extract the abstract from the designated section
            abstract_tag = soup.find("div", class_="paper-abstract")
            if abstract_tag:
                # The abstract is within a <p> tag inside the div
                abstract_paragraph = abstract_tag.find("p")
                return abstract_paragraph.text.strip() if abstract_paragraph else "Abstract not found."
            else:
                return "Abstract section not found."
        else:
            return "Failed to retrieve abstract."
    except requests.RequestException:
        return "Request to paper page failed."

def fetch_images_from_arxiv_html(paper_url):
    # Construct the corresponding HTML preview URL
    html_preview_url = paper_url.replace("html", "pdf")  # Adjust based on actual URL structure
    try:
        response = requests.get(html_preview_url, timeout=5)
        if response.status_code == 200:
            data = response.text
            soup = BeautifulSoup(data, "html.parser")

            # Extract images from the figure tags
            images = []
            for figure in soup.find_all("figure"):
                img_tag = figure.find("img")
                if img_tag and img_tag.has_attr("src"):
                    img_src = img_tag["src"]
                    img_url = urljoin(paper_url, img_src)
                    images.append(img_url)

            return images
        else:
            return []
    except requests.RequestException:
        return []

if __name__ == "__main__":
    app.run(debug=True)
