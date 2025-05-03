# 🗂️ Document Harvesting Assignment

## 📌 Overview

This project is designed to **crawl web pages**, **download documents** (PDF, HTML, EPUB), **extract text and metadata**, and store the data in a structured format (`.json` and `.txt`). It also includes **delta processing**, which ensures only new or updated documents are reprocessed using HTTP headers (`ETag`, `Last-Modified`) and content checksums.

---

## ⚙️ Features

- ✅ Crawl and parse web pages starting from a base URL  
- ✅ Download documents and skip unsupported types  
- ✅ Generate unique filenames for all resources  
- ✅ Extract metadata and compute SHA-256 checksums  
- ✅ Extract text from PDF, EPUB, and HTML files  
- ✅ Store extracted text and metadata in structured files  
- ✅ Skip unchanged files using delta processing  
- ✅ Handle password-protected PDFs and log errors  

---

## 🏗️ Project Structure

```
project/
│
├── Data Harvest/
|   └── downloads/  
|       ├── epubs/  # epubs downloads
|       ├── html/   # html downloads
|       ├── pdfs/   # pdfs downloads
|   ├── json/       # json stored per downloads
|   ├── text/       # text extracted from the pdfs, epubs and html
|   └── src/           
|       ├── configs.py/          # Configuration
|       ├── crawler.py/          # Handles crawling and downloading
|       ├── metadata_utiles.py/  # extract metadata
|       ├── text_extraction.py/  # extract text from the files
|       ├── utils.py/            # helper functions
|   └── main.py            # Coordinates processing and text/metadata extraction
├── .gitignore/        
└── requirements.txt   # Python dependencies
```

---

## 🚀 How to Run

### 1. **Clone the repository**
```bash
git clone https://github.com/AbbasKothari1552/Web-Scraping.git
cd document-harvesting
```

### 2. **Install dependencies**
   #### i. install libraries 
   ```bash
   pip install -r requirements.txt
   ```

   #### ii. Tesseract OCR Setup (Required for some PDFs)
   -> Install Tesseract: <br>
      Download from: https://github.com/tesseract-ocr/tesseract <br>
   -> Set Tesseract path in `configs.py` 
      ```python
      TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
      ```

   #### iii. Poppler Setup (Required for pdf2image OCR support)
   -> Install Poppler: <br>
      Download from: https://github.com/oschwartz10612/poppler-windows/releases <br>
      Extract it to a folder like `C:\poppler` <br>
      Add the `bin` directory (e.g., `C:\poppler\bin`) to your system `PATH`.
   

### 3. **Set the base URL**
Go to Data Harvest folder to access main.py
```bash
cd "Data Harvest"
```

Edit `main.py` to set your `BASE_URL`:
```python
BASE_URL = "https://example.com"
```

### 4. **Run the assignment**
```bash
python main.py
```

---

## 🔄 Workflow Summary

1. **Crawling**:
   - Starts from a base URL.
   - Collects internal page links and document download links.

2. **Downloading**:
   - Downloads supported file types.
   - Skips files already downloaded (using filename).
   - Checks for updates using ETag and Last-Modified headers.

3. **Processing**:
   - Generates metadata: filename, checksum, headers, etc.
   - Extracts text and saves as `.txt`.
   - Saves metadata as `.json`.

4. **Delta Processing**:
   - On subsequent runs, skips documents if not modified.


---


## ❗ Notes

- Some PDFs may be password-protected and will be skipped gracefully.
- Only PDF, EPUB, and HTML files are supported.