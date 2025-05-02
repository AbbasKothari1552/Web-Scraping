# utils.py
import hashlib
import re
import urllib.robotparser
from urllib.parse import urlparse

def is_allowed(url, user_agent='*'):
    try:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{base_url}/robots.txt")
        rp.read()
        return rp.can_fetch(user_agent, url)
    except:
        return True

def is_internal_link(base_url, link):
    try:
        base_domain = urlparse(base_url).netloc
        link_domain = urlparse(link).netloc
        return not link_domain or link_domain.lower() == base_domain.lower()
    except:
        return False

def should_download_file(link):
    return link.lower().endswith(('.pdf', '.epub', '.html'))

def generate_unique_filename(url, ext):
    hash_digest = hashlib.sha256(url.encode()).hexdigest()[:10]
    domain = urlparse(url).netloc.replace('.', '_')
    return f"{domain}_{hash_digest}.{ext}"
