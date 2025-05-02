# main.py
from src.crawler import run_crawler
from src.metadata_utils import extract_metadata, compute_sha256, save_metadata
from src.text_extraction import extract_text_from_pdf
import os

from src.configs import USER_AGENT, TEXT_DIR, DOWNLOAD_DIR


BASE_URL = "https://sanskritdocuments.org/scannedbooks/asisanskritpdfs.html"


def process_file(file_path, url):
    ext = file_path.split('.')[-1].lower()
    sha256 = compute_sha256(file_path)
    document_id = f"{ext}_{sha256[:8]}"
    
    domain = url.split('/')[2].replace('.', '_')
    base = os.path.basename(file_path).split('.')[0]

    metadata = extract_metadata(file_path, ext)
    metadata.update({
        'checksum': sha256,
        'document_id': document_id,
        'download_url': url,
        'file_path': file_path,
    })

    if ext == "pdf":
        os.makedirs(TEXT_DIR, exist_ok=True)
        text_filename = f"{domain}__{base}__{sha256[:8]}.txt"
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
