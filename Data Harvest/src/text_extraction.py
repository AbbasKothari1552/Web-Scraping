import os
from pdfminer.high_level import extract_text as extract_pdf_text
from pdf2image import convert_from_path
import pytesseract
import hashlib
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .configs import TESSERACT_PATH, OCR_LANGUAGES

# Set the tesseract path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def has_embedded_text(pdf_path, check_pages=3):
    try:
        text = extract_pdf_text(pdf_path, maxpages=check_pages)
        return len(text.strip()) > 50  # Threshold for real text
    except:
        return False


def extract_text_with_ocr(pdf_path, txt_path):
    pages = convert_from_path(pdf_path)
    with open(txt_path, 'w', encoding='utf-8') as out_file:
        for i, page in enumerate(pages):
            text = pytesseract.image_to_string(page, lang=OCR_LANGUAGES)
            out_file.write(f"\n\n--- Page {i+1} ---\n{text.strip()}")
            print(f"[OCR] Processed page {i+1}/{len(pages)}")


def extract_text_from_pdf(pdf_path, txt_output_path):
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


if __name__ == "__main__":
    import sys
    import json
    from configs import TEXT_DIR, JSON_DIR, TESSERACT_PATH, OCR_LANGUAGES
    from metadata_utils import compute_sha256, save_metadata, extract_metadata
    import os

    if len(sys.argv) < 2:
        print("Usage: python text_extraction.py <path_to_pdf>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    filename = os.path.basename(file_path)
    filename = os.path.splitext(filename)[0]
    ext = file_path.split('.')[-1].lower()

    text_filename = f"{filename}.txt"
    text_output_path = os.path.join(TEXT_DIR, text_filename)

    if os.path.exists(text_output_path):
        print("file already generated")
        sys.exit(1)

    # Extract text to file
    os.makedirs(TEXT_DIR, exist_ok=True)
    extract_text_from_pdf(file_path, text_output_path)

    # Attempt to locate existing metadata JSON
    os.makedirs(JSON_DIR, exist_ok=True)
    json_path = os.path.join(JSON_DIR, f"{filename}.json")

    if os.path.exists(json_path):
        print(f"[Update] Found metadata JSON: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        print(f"[Create] No metadata found. Creating new metadata.")
        metadata = extract_metadata(file_path, ext)

    metadata['content'] = text_output_path
    save_metadata(metadata, output_dir=JSON_DIR)
