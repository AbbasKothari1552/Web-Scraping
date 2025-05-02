# crawler.py
import os
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from .utils import is_allowed, is_internal_link, should_download_file, generate_unique_filename


VISITED = set()


def setup_download_directories(base_path):
    os.makedirs(os.path.join(base_path, "pdfs"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "epubs"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "html"), exist_ok=True)
    return base_path


def download_file(url, download_dir, user_agent):
    try:
        response = requests.head(url, headers={'User-Agent': user_agent}, allow_redirects=True)
        content_type = response.headers.get("Content-Type", "").lower()
        ext = url.split('.')[-1].split("?")[0].lower()

        if ext == "pdf":
            subdir = "pdfs"
        elif ext == "epub":
            subdir = "epubs"
        elif "text/html" in content_type:
            ext = "html"
            subdir = "html"
        else:
            print(f"[Skip] Unsupported file type: {url}")
            return None

        filename = generate_unique_filename(url, ext)
        path = os.path.join(download_dir, subdir, filename)

        if os.path.exists(path):
            print(f"[Skip] Already downloaded: {path}")
            return path

        print(f"[Downloading] {url} → {path}")
        file_resp = requests.get(url, headers={'User-Agent': user_agent})
        file_resp.raise_for_status()

        with open(path, "wb") as f:
            f.write(file_resp.content)

        return path

    except Exception as e:
        print(f"[Error] Failed to download {url} | Reason: {e}")
        return None


def classify_links(base_url, soup):
    crawl_links = set()
    download_links = set()

    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        if should_download_file(href):
            download_links.add(href)
        elif is_internal_link(base_url, href):
            crawl_links.add(href)
    return crawl_links, download_links


def crawl(url, base_url, user_agent, visited, download_dir, downloaded_files):
    if url in visited:
        return
    visited.add(url)

    if not is_allowed(url, user_agent):
        print(f"[Blocked] robots.txt blocked: {url}")
        return

    try:
        response = requests.get(url, headers={'User-Agent': user_agent})
        response.raise_for_status()
    except Exception as e:
        print(f"[Error] Failed to crawl {url} | Reason: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    crawl_links, download_links = classify_links(base_url, soup)

    # save HTML
    download_file(url, download_dir, user_agent)

    for dlink in download_links:
        file_path = download_file(dlink, download_dir, user_agent)
        if file_path:
            downloaded_files.append((file_path, dlink))
        time.sleep(2)

    for clink in crawl_links:
        time.sleep(2)
        crawl(clink, base_url, user_agent, visited, download_dir, downloaded_files)


def run_crawler(base_url, download_dir, user_agent):
    setup_download_directories(download_dir)
    downloaded_files = []
    crawl(base_url, base_url, user_agent, VISITED, download_dir, downloaded_files)
    return downloaded_files


if __name__ == "__main__":
    print("[Start] Crawling and downloading...")
    run_crawler()
    print("[Done] Crawl completed.")
