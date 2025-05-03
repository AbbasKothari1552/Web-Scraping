"""
main.py
The primary entry point for the data harvesting pipeline. Orchestrates crawling, downloading, metadata extraction,
and text processing for PDF, EPUB, and HTML documents.

Workflow:
1. Initiates crawler to discover and download files
2. Processes each file to extract metadata and text content
3. Saves structured metadata to JSON files
4. Stores extracted text in separate files

Dependencies:
    src.crawler - For web crawling and downloading
    src.metadata_utils - For metadata extraction and processing
    src.text_extraction - For content extraction from files
    datetime - For timestamp generation
    os - For filesystem operations
"""


from src.crawler import run_crawler
from src.metadata_utils import extract_metadata, compute_sha256, save_metadata
from src.text_extraction import extract_text_from_pdf, extract_text_from_epub, extract_text_from_html
from datetime import datetime
import os

from src.configs import USER_AGENT, TEXT_DIR, DOWNLOAD_DIR, JSON_DIR
from src.metadata_utils import format_as_iso8601

# Base URL to begin crawling
BASE_URL = "https://sample-files.com/documents/pdf/"


def process_file(file_path, url, last_modified=None, etag=None):
    """
    Processes a single downloaded file to extract metadata and text content.
    
    Args:
        file_path (str): Path to the downloaded file
        url (str): Source URL of the file
        last_modified (str, optional): Last-Modified header from HTTP response
        etag (str, optional): ETag header from HTTP response
        
    Workflow:
        1. Computes file checksum
        2. Extracts metadata
        3. Performs text extraction based on file type
        4. Saves complete metadata record
        
    Example:
        >>> process_file("downloads/pdfs/doc1.pdf", "https://example.com/doc1.pdf")
        [Creates metadata JSON and extracted text file]
    """

    # Generate SHA-256 checksum for file integrity
    sha256 = compute_sha256(file_path)

    # Prepare file identifiers
    filename = os.path.basename(file_path)
    filename = os.path.splitext(filename)[0]
    ext = file_path.split('.')[-1].lower()

    # Set up text output path
    text_filename = f"{filename}.txt"
    text_output_path = os.path.join(TEXT_DIR, text_filename)

    # Extract metadata
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

    # Ensure text output directory exists
    os.makedirs(TEXT_DIR, exist_ok=True)

    try:
        # Route to appropriate text extractor based on file type
        if ext == "pdf":
            extract_text_from_pdf(file_path, text_output_path)
            metadata['content'] = text_output_path
        elif ext == "html":
            extract_text_from_html(file_path, text_output_path)
            metadata['content'] = text_output_path
        elif ext == "epub":
            extract_text_from_epub(file_path, text_output_path)
            metadata['content'] = text_output_path

        # Save complete metadata record
        save_metadata(metadata, JSON_DIR)
        
    except Exception as e:
        print(f"[Error] Failed to extract text from {file_path} | Reason: {e}")

def main():
    """
    Main execution function for the harvesting pipeline.
    
    Workflow:
        1. Initiates crawler with base URL
        2. Processes all downloaded files
        3. Outputs completion status
    """

    # Run crawler and get list of downloaded files
    print("[Start] Harvesting process")
    downloaded_files = run_crawler(BASE_URL, DOWNLOAD_DIR, USER_AGENT)

    # Ensure text output directory exists
    os.makedirs(TEXT_DIR, exist_ok=True)

    # Process each downloaded file
    for file_path, url, last_modified, etag in downloaded_files:
        process_file(file_path, url, last_modified, etag)

    print("[Done] All files processed.")



if __name__ == "__main__":
    # Entry point when run as standalone script
    main()
