# src/config.py

import os

# === Scraper Settings ===
USER_AGENT = "MyEduScraper/1.0 (Educational Project)"

# === Directory Paths ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')
TEXT_DIR = os.path.join(BASE_DIR, 'text')
JSON_DIR = os.path.join(BASE_DIR, 'json')

PDF_DIR = os.path.join(DOWNLOAD_DIR, 'pdfs')
EPUB_DIR = os.path.join(DOWNLOAD_DIR, 'epubs')
HTML_DIR = os.path.join(DOWNLOAD_DIR, 'html')

# === OCR Configuration ===
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
OCR_LANGUAGES = "eng+san"
