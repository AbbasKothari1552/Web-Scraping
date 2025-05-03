"""
configs.py
Central configuration file for the data harvesting system. Contains all settings and paths used across the application.

Configuration Sections:
1. Scraper Settings - User agent and crawling behavior
2. Directory Paths - Filesystem locations for downloaded and processed files
3. OCR Configuration - Tesseract OCR settings and language support

Note: Paths are constructed relative to the project root directory for portability.

Dependencies:
    os - For path manipulation and directory operations
"""

import os

# === Scraper Settings ===
USER_AGENT = "MyEduScraper/1.0 (Educational Project)"
"""
User agent string for HTTP requests. 
Follows format: <ApplicationName>/<Version> (<Additional Comments>)

Used to:
- Identify the scraper to web servers
- Comply with robots.txt policies
- Some sites require specific user agents for access
"""

# === Directory Paths ===
# Base directory is one level above src/ (project root)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Main storage directories
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')
"""
Parent directory for all downloaded files.
Structure:
    downloads/
    ├── pdfs/
    ├── epubs/
    └── html/
"""

TEXT_DIR = os.path.join(BASE_DIR, 'text')
"""
Directory for extracted text content.
Files are stored as <document_id>.txt
"""

JSON_DIR = os.path.join(BASE_DIR, 'json')
"""
Directory for metadata JSON files.
Files are stored as <document_id>.json
"""

# Subdirectories for specific file types
PDF_DIR = os.path.join(DOWNLOAD_DIR, 'pdfs')
"""PDF downloads storage (subdirectory of downloads/)"""

EPUB_DIR = os.path.join(DOWNLOAD_DIR, 'epubs')
"""EPUB downloads storage (subdirectory of downloads/)"""

HTML_DIR = os.path.join(DOWNLOAD_DIR, 'html')
"""HTML downloads storage (subdirectory of downloads/)"""

# === OCR Configuration ===
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
"""
Absolute path to Tesseract OCR executable.
Note: This Windows-specific path should be modified for:
- Linux/macOS systems (typically '/usr/bin/tesseract')
- Custom Tesseract installations
"""

OCR_LANGUAGES = "eng+san"
"""
Languages for OCR processing, in Tesseract format:
- 'eng' for English
- 'san' for Sanskrit
Multiple languages are joined with '+'

Important: Requires corresponding trained data files to be installed.
"""