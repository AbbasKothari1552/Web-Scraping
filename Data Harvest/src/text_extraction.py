import os
from pdfminer.high_level import extract_text as extract_pdf_text
from pdf2image import convert_from_path
import pytesseract
import hashlib


# Set the tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


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
            text = pytesseract.image_to_string(page, lang='eng+san')
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

