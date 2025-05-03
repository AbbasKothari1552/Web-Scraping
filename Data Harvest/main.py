# main.py
from src.crawler import run_crawler
from src.metadata_utils import extract_metadata, compute_sha256, save_metadata
from src.text_extraction import extract_text_from_pdf, extract_text_from_epub, extract_text_from_html
from datetime import datetime
import os

from src.configs import USER_AGENT, TEXT_DIR, DOWNLOAD_DIR, JSON_DIR
from src.metadata_utils import format_as_iso8601


BASE_URL = "https://sample-files.com/documents/pdf/"


def process_file(file_path, url, last_modified=None, etag=None):
    sha256 = compute_sha256(file_path)

    filename = os.path.basename(file_path)
    filename = os.path.splitext(filename)[0]
    ext = file_path.split('.')[-1].lower()

    text_filename = f"{filename}.txt"
    text_output_path = os.path.join(TEXT_DIR, text_filename)

    metadata = extract_metadata(file_path, ext, url)
    metadata.update({
        'checksum': sha256,
        'document_id': filename,
        'download_url': url,
        'file_path': file_path,
        'scraped_at': datetime.now().isoformat(),  # Add timestamp
        'pub_year': format_as_iso8601(metadata.get('pub_year', 'N/A')),  # New function
        'last_modified': last_modified,
        'etag': etag,
    })

    os.makedirs(TEXT_DIR, exist_ok=True)

    try:
        # Text extraction based on file type
        if ext == "pdf":
            extract_text_from_pdf(file_path, text_output_path)
            metadata['content'] = text_output_path
        elif ext == "html":
            extract_text_from_html(file_path, text_output_path)
            metadata['content'] = text_output_path
        elif ext == "epub":
            extract_text_from_epub(file_path, text_output_path)
            metadata['content'] = text_output_path

        save_metadata(metadata, JSON_DIR)
        
    except Exception as e:
        print(f"[Error] Failed to extract text from {file_path} | Reason: {e}")

def main():
    print("[Start] Harvesting process")
    downloaded_files = run_crawler(BASE_URL, DOWNLOAD_DIR, USER_AGENT)

    os.makedirs(TEXT_DIR, exist_ok=True)

    for file_path, url, last_modified, etag in downloaded_files:
        process_file(file_path, url, last_modified, etag)

    print("[Done] All files processed.")



if __name__ == "__main__":
    main()
