import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
import os

# For PDF/EPUB/HTML downloads
from pathlib import Path

from crawler import WebCrawler
from src.configs import ScraperConfig


config = ScraperConfig()
crawler = WebCrawler(config=config)

url = "https://sanskritdocuments.org/scannedbooks/asisanskritpdfs.html"

crawler.crawl(url)





