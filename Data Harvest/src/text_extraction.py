"""
text_extraction.py
Text extraction utilities for document files (PDF, EPUB, HTML) with OCR fallback.

Key Functionality:
- Extracts text from PDFs (both embedded text and via OCR)
- Processes EPUB documents by extracting all textual content
- Parses HTML files to extract clean text
- Handles both digital-born and scanned PDFs
- Supports multilingual OCR (English + Sanskrit)

Dependencies:
    pdfminer - Embedded PDF text extraction
    pdf2image - PDF to image conversion for OCR
    pytesseract - OCR text recognition
    ebooklib - EPUB parsing
    BeautifulSoup - HTML parsing
"""

import os
from pdfminer.high_level import extract_text as extract_pdf_text
from pdf2image import convert_from_path
from ebooklib import epub
from bs4 import BeautifulSoup
import pytesseract
import hashlib
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .configs import TESSERACT_PATH, OCR_LANGUAGES

# Configure Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def has_embedded_text(pdf_path, check_pages=3):
    """
    Checks if a PDF contains selectable/embedded text.
    
    Args:
        pdf_path (str): Path to PDF file
        check_pages (int): Number of pages to sample (default: 3)
        
    Returns:
        bool: True if sufficient embedded text found
        
    Note:
        Uses a threshold of 50 characters to determine if text is meaningful
    """

    try:
        text = extract_pdf_text(pdf_path, maxpages=check_pages)
        return len(text.strip()) > 50  # Threshold for real text
    except:
        return False


def extract_text_with_ocr(pdf_path, txt_path):
    """
    Extracts text from scanned PDFs using OCR.
    
    Args:
        pdf_path (str): Path to PDF file
        txt_path (str): Output text file path
        
    Process:
        1. Converts PDF pages to images
        2. Applies OCR to each image
        3. Saves results with page demarcations
        
    Note:
        Uses language settings from configs.OCR_LANGUAGES
    """

    pages = convert_from_path(pdf_path)
    with open(txt_path, 'w', encoding='utf-8') as out_file:
        for i, page in enumerate(pages):
            text = pytesseract.image_to_string(page, lang=OCR_LANGUAGES)
            out_file.write(f"\n\n--- Page {i+1} ---\n{text.strip()}")
            print(f"[OCR] Processed page {i+1}/{len(pages)}")


def extract_text_from_pdf(pdf_path, txt_output_path):
    """
    Main PDF text extraction function with automatic OCR fallback.
    
    Args:
        pdf_path (str): Path to input PDF
        txt_output_path (str): Path for output text file
        
    Workflow:
        1. Checks for existing embedded text
        2. If found, extracts directly
        3. If not, falls back to OCR processing
        
    Note:
        Skips processing if output file already exists
    """

    if os.path.exists(txt_output_path):
        print(f"[Skip] Text already extracted: {txt_output_path}")
        return

    if has_embedded_text(pdf_path):
        print("[INFO] Extracting embedded text...")
        text = extract_pdf_text(pdf_path)
        with open(txt_output_path, 'w', encoding='utf-8') as f:
            f.write(text.strip())
    else:
        print("[INFO] No embedded text found. Running OCR...")
        extract_text_with_ocr(pdf_path, txt_output_path)

    print(f"[Saved] Full text to: {txt_output_path}")


def extract_text_from_html(html_path, output_path):
    """
    Extracts clean text from HTML files.
    
    Args:
        html_path (str): Path to HTML file
        output_path (str): Output text file path
        
    Process:
        1. Parses HTML with BeautifulSoup
        2. Extracts all text with newline separators
        3. Removes excess whitespace and markup
        
    Note:
        Preserves basic paragraph structure but removes all HTML tags
    """
     
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"[Extracted] HTML text saved to: {output_path}")
    except Exception as e:
        print(f"[Error] Failed to extract HTML text: {e}")


def extract_text_from_epub(epub_path, output_path):
    """
    Extracts text content from EPUB files.
    
    Args:
        epub_path (str): Path to EPUB file
        output_path (str): Output text file path
        
    Process:
        1. Parses EPUB structure
        2. Extracts text from all document items
        3. Joins content with double newlines between sections
        
    Note:
        Handles both XHTML and HTML content within EPUBs
    """
    
    try:
        book = epub.read_epub(epub_path)
        all_text = []

        for item in book.get_items():
            if item.get_type() == epub.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text = soup.get_text(separator='\n', strip=True)
                all_text.append(text)

        full_text = '\n\n'.join(all_text)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"[Extracted] EPUB text saved to: {output_path}")
    except Exception as e:
        print(f"[Error] Failed to extract EPUB text: {e}")


# if __name__ == "__main__":
#     import sys
#     import json
#     from configs import TEXT_DIR, JSON_DIR, TESSERACT_PATH, OCR_LANGUAGES
#     from metadata_utils import compute_sha256, save_metadata, extract_metadata
#     import os

#     if len(sys.argv) < 2:
#         print("Usage: python text_extraction.py <path_to_pdf>")
#         sys.exit(1)

#     file_path = sys.argv[1]

#     if not os.path.exists(file_path):
#         print(f"Error: File not found: {file_path}")
#         sys.exit(1)

#     filename = os.path.basename(file_path)
#     filename = os.path.splitext(filename)[0]
#     ext = file_path.split('.')[-1].lower()

#     text_filename = f"{filename}.txt"
#     text_output_path = os.path.join(TEXT_DIR, text_filename)

#     if os.path.exists(text_output_path):
#         print("file already generated")
#         sys.exit(1)

#     # Extract text to file
#     os.makedirs(TEXT_DIR, exist_ok=True)
#     extract_text_from_pdf(file_path, text_output_path)

#     # Attempt to locate existing metadata JSON
#     os.makedirs(JSON_DIR, exist_ok=True)
#     json_path = os.path.join(JSON_DIR, f"{filename}.json")

#     if os.path.exists(json_path):
#         print(f"[Update] Found metadata JSON: {json_path}")
#         with open(json_path, 'r', encoding='utf-8') as f:
#             metadata = json.load(f)
#     else:
#         print(f"[Create] No metadata found. Creating new metadata.")
#         metadata = extract_metadata(file_path, ext)

#     metadata['content'] = text_output_path
#     save_metadata(metadata, output_dir=JSON_DIR)
