# main.py
from src.crawler import run_crawler
from src.metadata_utils import extract_metadata, compute_sha256, save_metadata
from src.text_extraction import extract_text_from_pdf
import os

from src.configs import USER_AGENT, TEXT_DIR, DOWNLOAD_DIR


BASE_URL = "https://sample-files.com/documents/pdf/"


def process_file(file_path, url):
    sha256 = compute_sha256(file_path)

    filename = os.path.basename(file_path)
    filename = os.path.splitext(filename)[0]
    ext = file_path.split('.')[-1].lower()

    text_filename = f"{filename}.txt"
    text_output_path = os.path.join(TEXT_DIR, text_filename)

    metadata = extract_metadata(file_path, ext)
    metadata.update({
        'checksum': sha256,
        'document_id': filename,
        'download_url': url,
        'file_path': file_path,
    })

    if ext == "pdf":
        os.makedirs(TEXT_DIR, exist_ok=True)
        text_filename = f"{filename}.txt"
        text_output_path = os.path.join(TEXT_DIR, text_filename)
        extract_text_from_pdf(file_path, text_output_path)
        metadata['content'] = text_output_path  # Add only if text is extracted

    save_metadata(metadata)


def main():
    print("[Start] Harvesting process")
    downloaded_files = run_crawler(BASE_URL, DOWNLOAD_DIR, USER_AGENT)

    os.makedirs(TEXT_DIR, exist_ok=True)

    for file_path, url in downloaded_files:
        process_file(file_path, url)

    print("[Done] All files processed.")



if __name__ == "__main__":
    main()
