"""
crawler.py
Web crawling and file downloading module for the data harvesting system.

Key Features:
- Recursive crawling of internal links
- Smart file downloading with duplicate prevention
- Respect for robots.txt rules
- Delta processing using ETag/Last-Modified headers
- Directory structure management

Workflow:
1. Starts from base URL and discovers links
2. Classifies links as either crawlable or downloadable
3. Downloads supported file types (PDF, EPUB, HTML)
4. Tracks visited URLs to prevent loops

Dependencies:
    requests - For HTTP requests
    BeautifulSoup - For HTML parsing
    urllib.parse - For URL manipulation
    os - For filesystem operations
    time - For crawl delays
    json - For metadata handling
"""

import os
import time
import requests
import json
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from .utils import is_allowed, is_internal_link, should_download_file, generate_unique_filename
from .configs import JSON_DIR

# Global set to track visited URLs and prevent duplicate processing
VISITED = set()


def setup_download_directories(base_path):
    """
    Creates the directory structure for downloaded files.
    
    Args:
        base_path (str): Root download directory path
        
    Returns:
        str: The created base path
        
    Directory Structure Created:
        base_path/
        ├── pdfs/
        ├── epubs/
        └── html/
    """

    # Ensure parent directory exists
    os.makedirs(base_path, exist_ok=True)

    # Create subdirectories
    os.makedirs(os.path.join(base_path, "pdfs"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "epubs"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "html"), exist_ok=True)

    return base_path


def download_file(url, download_dir, user_agent):
    """
    Downloads a file with smart duplicate detection and delta processing.
    
    Args:
        url (str): URL of the file to download
        download_dir (str): Base download directory
        user_agent (str): User agent string for requests
        
    Returns:
        tuple: (file_path, last_modified, etag) or (None, None, None) if skipped
        
    Workflow:
        1. Checks file type (PDF/EPUB/HTML)
        2. Verifies if unchanged using ETag/Last-Modified
        3. Downloads if new or modified
        4. Returns metadata for processing
    """
    try:
        # Step 1: Send HEAD request to get metadata
        head_resp = requests.head(url, headers={'User-Agent': user_agent}, allow_redirects=True)
        content_type = head_resp.headers.get("Content-Type", "").lower()
        last_modified = head_resp.headers.get("Last-Modified")
        etag = head_resp.headers.get("ETag")
        ext = url.split('.')[-1].split("?")[0].lower()

        # Determine file type and subdirectory
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
        
        # Generate unique filename and paths
        filename = generate_unique_filename(url, ext)
        path = os.path.join(download_dir, subdir, filename)

        # Step 2: Check for existing file and metadata
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

                # Step 3: Skip if file hasn't changed
                if (etag and etag == prev_etag) or (last_modified and last_modified == prev_last_modified):
                    print(f"[Skip] Not modified: {url}")
                    return None, None, None
                
        # Step 4: Download the file
        print(f"[Downloading] {url} → {path}")
        file_resp = requests.get(url, headers={'User-Agent': user_agent})
        file_resp.raise_for_status()

        with open(path, "wb") as f:
            f.write(file_resp.content)

        # Step 5: Return metadata for processing
        return path, last_modified, etag

    except Exception as e:
        print(f"[Error] Failed to download {url} | Reason: {e}")
        return None, None, None


def classify_links(base_url, soup):
    """
    Categorizes links from a webpage into crawlable and downloadable.
    
    Args:
        base_url (str): Root URL for determining internal links
        soup (BeautifulSoup): Parsed HTML content
        
    Returns:
        tuple: (set of crawl_links, set of download_links)
    """

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
    """
    Recursive web crawler that processes pages and downloads files.
    
    Args:
        url (str): Current URL to process
        base_url (str): Root domain for link classification
        user_agent (str): User agent string
        visited (set): Track visited URLs
        download_dir (str): Base download directory
        downloaded_files (list): Accumulator for downloaded files
        
    Notes:
        - Implements 2-second delay between requests
        - Respects robots.txt rules
        - Skips already visited URLs
    """

    if url in visited:
        return
    visited.add(url)

    if not is_allowed(url, user_agent):
        print(f"[Blocked] robots.txt blocked: {url}")
        return
    
    # Polite crawling delay
    time.sleep(2)
    try:
        response = requests.get(url, headers={'User-Agent': user_agent})
        response.raise_for_status()
    except Exception as e:
        print(f"[Error] Failed to crawl {url} | Reason: {e}")
        return

    # Parse and classify links
    soup = BeautifulSoup(response.text, 'html.parser')
    crawl_links, download_links = classify_links(base_url, soup)

    # Save HTML content if this is an HTML page
    download_file(url, download_dir, user_agent)

    print("Download_links count:", len(download_links))
    print("crawl_links count:", len(crawl_links))

    # Process download links
    for dlink in download_links:
        file_path, last_modified, etag = download_file(dlink, download_dir, user_agent)
        if file_path:
            downloaded_files.append((file_path, dlink, last_modified, etag))
        time.sleep(2) # Delay between downloads

    # Process all the internal links recursively
    for clink in crawl_links:
        time.sleep(2)
        crawl(clink, base_url, user_agent, visited, download_dir, downloaded_files)


def run_crawler(base_url, download_dir, user_agent):
    """
    Main crawler entry point.
    
    Args:
        base_url (str): Starting URL for crawling
        download_dir (str): Base directory for downloads
        user_agent (str): User agent string
        
    Returns:
        list: Downloaded files with metadata (path, url, last_modified, etag)
    """

    # Initialize directory structure
    setup_download_directories(download_dir)

    # Start crawling
    downloaded_files = []
    crawl(base_url, base_url, user_agent, VISITED, download_dir, downloaded_files)
    return downloaded_files


# if __name__ == "__main__":
#     from .configs import USER_AGENT, DOWNLOAD_DIR
#     BASE_URL = "https://sample-files.com/documents/pdf/"
#     run_crawler(BASE_URL, DOWNLOAD_DIR, USER_AGENT)

