# crawler.py
import os
import time
import requests
import json
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from .utils import is_allowed, is_internal_link, should_download_file, generate_unique_filename
from .configs import JSON_DIR

VISITED = set()


def setup_download_directories(base_path):
    # Ensure parent directory
    os.makedirs(base_path, exist_ok=True)

    # Create subdirectories
    os.makedirs(os.path.join(base_path, "pdfs"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "epubs"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "html"), exist_ok=True)

    return base_path


def download_file(url, download_dir, user_agent):
    try:
        # Step 1: Send HEAD request
        head_resp = requests.head(url, headers={'User-Agent': user_agent}, allow_redirects=True)
        content_type = head_resp.headers.get("Content-Type", "").lower()
        last_modified = head_resp.headers.get("Last-Modified")
        etag = head_resp.headers.get("ETag")
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
            return None, None, None
        
        filename = generate_unique_filename(url, ext)
        path = os.path.join(download_dir, subdir, filename)

        # Step 2: Check if file and metadata already exist
        json_path = os.path.join(JSON_DIR, f"{os.path.splitext(filename)[0]}.json")
        print("file Path:", path)
        print("json Path:", json_path)
        print("file Path:", os.path.exists(path))
        print("json Path:", os.path.exists(json_path))

        if os.path.exists(path) and os.path.exists(json_path):
            print(True)
            with open(json_path, "r") as f:
                metadata = json.load(f)
                prev_etag = metadata.get("etag")
                prev_last_modified = metadata.get("last_modified")

                # Step 3: If server provides ETag or Last-Modified, compare
                if (etag and etag == prev_etag) or (last_modified and last_modified == prev_last_modified):
                    print(f"[Skip] Not modified: {url}")
                    return None, None, None
                
        # Step 4: Download the file
        print(f"[Downloading] {url} → {path}")
        file_resp = requests.get(url, headers={'User-Agent': user_agent})
        file_resp.raise_for_status()

        with open(path, "wb") as f:
            f.write(file_resp.content)

        # Step 5: Return extra info needed for metadata
        return path, last_modified, etag

    except Exception as e:
        print(f"[Error] Failed to download {url} | Reason: {e}")
        return None, None, None


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
    
    # Add delay before crawling a new page
    time.sleep(2)
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

    print("Download_links count:", len(download_links))
    print("crawl_links count:", len(crawl_links))

    for dlink in download_links:
        file_path, last_modified, etag = download_file(dlink, download_dir, user_agent)
        if file_path:
            downloaded_files.append((file_path, dlink, last_modified, etag))
        time.sleep(2)

    # for clink in crawl_links:
    #     time.sleep(2)
    #     crawl(clink, base_url, user_agent, visited, download_dir, downloaded_files)


def run_crawler(base_url, download_dir, user_agent):
    setup_download_directories(download_dir)
    downloaded_files = []
    crawl(base_url, base_url, user_agent, VISITED, download_dir, downloaded_files)
    return downloaded_files


# if __name__ == "__main__":
#     from .configs import USER_AGENT, DOWNLOAD_DIR
#     BASE_URL = "https://sample-files.com/documents/pdf/"
#     run_crawler(BASE_URL, DOWNLOAD_DIR, USER_AGENT)

