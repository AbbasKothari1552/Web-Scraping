from PyPDF2 import PdfReader
from ebooklib import epub
from pdfminer.high_level import extract_text
from langdetect import detect
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import hashlib
import json
import os


def extract_metadata(file_path, file_type, url=None):
    metadata = {}
    if file_type == "pdf":
        metadata = extract_pdf_info(file_path)
    elif file_type == "epub":
        metadata = extract_epub_info(file_path)
    elif file_type == "html":
        metadata = extract_html_info(file_path)

    # Extract site from URL (e.g., "ayushportal.nic.in")
    if url:
        domain = urlparse(url).netloc
        metadata["site"] = domain

    return metadata


def extract_pdf_info(file_path):
    # Initialize default values
    title = "N/A"
    authors = []
    pub_year = "N/A"
    language = "N/A"

    # 1. Extract Metadata using PyPDF2
    try:
        with open(file_path, 'rb') as file:
            pdf = PdfReader(file)
            metadata = pdf.metadata

            if metadata:
                title = metadata.get('/Title', 'N/A')
                authors_raw = metadata.get('/Author', 'N/A')
                authors = normalize_authors(authors_raw)
    except Exception as e:
        print(f"Error reading metadata: {e}")

    # 2. Extract Text and Search for Year & Language
    try:
        text = extract_text(file_path)
        # Detect Language (if text is sufficient)
        try:
            language = detect(text[:1000])  # Check first 1000 chars for language
        except:
            language = "N/A"

        # Search for Publication Year (e.g., 2023, © 2020, "Published in 1999")
        year_matches = re.findall(r'(?:19|20)\d{2}', text)
        if year_matches:
            pub_year = max(set(year_matches), key=year_matches.count)  # Most frequent year
    except Exception as e:
        print(f"Error extracting text: {e}")

    return {
        'title': title,
        'authors': authors,
        'pub_year': pub_year,
        'language': language
    }


def extract_epub_info(file_path):
    title = "N/A"
    authors = []
    language = "N/A"
    pub_year = "N/A"

    try:
        date_meta = book.get_metadata('DC', 'date')
        if date_meta:
            pub_year = re.search(r'\d{4}', date_meta[0][0]).group(0)  # Extract first 4-digit year
    except:
        pass

    try:
        book = epub.read_epub(file_path)
        title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else "N/A"
        authors_raw = book.get_metadata('DC', 'creator')
        authors = normalize_authors(authors_raw[0][0] if authors_raw else "N/A")
        language = book.get_metadata('DC', 'language')[0][0] if book.get_metadata('DC', 'language') else "N/A"
    except Exception as e:
        print(f"[EPUB metadata error] {e}")

    return {
        'title': title,
        'authors': authors,
        'pub_year': pub_year,
        'language': language
    }

def extract_html_info(file_path):
    title = "N/A"
    authors = []
    language = "N/A"
    pub_year = "N/A"

    try:
        with open(file_path, "r", encoding='utf-8') as f:
            soup = BeautifulSoup(f, "html.parser")
            if soup.title:
                title = soup.title.string.strip()
            for meta in soup.find_all("meta"):
                if meta.get("name") in ["author", "dc.creator"]:
                    authors_raw = meta.get("content", "N/A")
                    authors = normalize_authors(authors_raw)
                if meta.get("name") == "language":
                    language = meta.get("content", "N/A")
            for meta in soup.find_all("meta"):
                if meta.get("name") in ["date", "publication_date"]:
                    pub_year = re.search(r'\d{4}', meta.get("content", "")).group(0)
            if pub_year == "N/A":
                year_matches = re.findall(r'(?:19|20)\d{2}', soup.get_text())
                if year_matches:
                    pub_year = max(set(year_matches), key=year_matches.count)
    except Exception as e:
        print(f"[HTML metadata error] {e}")

    return {
        'title': title,
        'authors': authors,
        'pub_year': pub_year,
        'language': language
    }


def format_as_iso8601(year_str):
    if year_str == "N/A" or not year_str.isdigit():
        return "N/A"
    return f"{year_str}-01-01"  # Default to January 1 if only year is known


def normalize_authors(authors_raw):
    if not authors_raw or authors_raw == "N/A":
        return []

    if isinstance(authors_raw, list):
        # EPUB returns list from ebooklib already
        authors_raw = " ".join(authors_raw)

    # Unified splitting: handle commas, semicolons, "and", "&"
    parts = re.split(r'\s*(?:,|;|\band\b|\&)\s*', authors_raw, flags=re.IGNORECASE)
    
    # Remove empty strings and title case (e.g., "john doe" -> "John Doe")
    return [part.strip().title() for part in parts if part.strip()]


def compute_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error computing SHA-256: {e}")
        return None
    

def save_metadata(metadata, output_dir="Data Harvest/json"):
    os.makedirs(output_dir, exist_ok=True)
    doc_id = metadata.get("document_id", "unknown")
    output_path = os.path.join(output_dir, f"{doc_id}.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    
    print(f"Saved metadata to {output_path}")


# if __name__ == "__main__":
#     import sys
#     from configs import JSON_DIR  # Add config import if needed

#     if len(sys.argv) < 2:
#         print("Usage: python metadata_utils.py <path_to_pdf>")
#         sys.exit(1)

#     file_path = sys.argv[1]

#     if not os.path.exists(file_path):
#         print(f"Error: File not found: {file_path}")
#         sys.exit(1)

#     filename = os.path.basename(file_path)
#     filename = os.path.splitext(filename)[0]
#     ext = file_path.split('.')[-1].lower()

#     json_path = os.path.join(JSON_DIR, f"{filename}.json")
#     if os.path.exists(json_path):
#         print("File already exists")
#         sys.exit(1)

#     metadata = extract_metadata(file_path, ext)
#     sha256 = compute_sha256(file_path)
#     metadata.update({
#         "document_id": filename,
#         "checksum": sha256,
#         "file_path": file_path,
#     })

#     save_metadata(metadata, output_dir=JSON_DIR)