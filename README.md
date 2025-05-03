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
├── crawler.py         # Handles crawling and downloading
├── main.py            # Coordinates processing and text/metadata extraction
├── extractors/        # Contains text and metadata extraction logic
├── output/
│   ├── pdfs/
│   ├── epubs/
│   ├── html/
│   ├── texts/
│   └── metadata/
└── requirements.txt   # Python dependencies
```

---

## 🚀 How to Run

### 1. **Clone the repository**
```bash
git clone https://github.com/yourusername/document-harvesting.git
cd document-harvesting
```

### 2. **Install dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Set the base URL**
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

## 🧪 Sample Output

- `output/pdfs/example_com_ab12cd34ef.pdf`
- `output/texts/example_com_ab12cd34ef.txt`
- `output/metadata/example_com_ab12cd34ef.json`

---

## ❗ Notes

- Some PDFs may be password-protected and will be skipped gracefully.
- Only PDF, EPUB, and HTML files are supported.
- Ensure stable internet connection for crawling.