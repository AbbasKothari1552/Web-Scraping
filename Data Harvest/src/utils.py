"""
Utility functions for handling URL checks, file naming, and download conditions.

This module provides helper functions used across the data harvesting pipeline
for tasks such as checking robots.txt permissions, determining file types,
generating unique filenames, and identifying internal links.
"""

import hashlib
import re
import urllib.robotparser
from urllib.parse import urlparse

def is_allowed(url, user_agent='*'):
    """
    Check if a URL is allowed to be crawled based on the site's robots.txt file.

    Args:
        url (str): The URL to check.
        user_agent (str): The user agent string to use (default is '*').

    Returns:
        bool: True if the URL is allowed to be fetched, False otherwise.
    """

    try:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{base_url}/robots.txt")
        rp.read()
        return rp.can_fetch(user_agent, url)
    except:
        # If robots.txt can't be fetched or parsed, allow by default
        return True

def is_internal_link(base_url, link):
    """
    Determine whether a link is internal to the base domain.

    Args:
        base_url (str): The root/base URL.
        link (str): The hyperlink to evaluate.

    Returns:
        bool: True if the link is internal or relative, False if it's an external domain.
    """
    try:
        base_domain = urlparse(base_url).netloc
        link_domain = urlparse(link).netloc
        return not link_domain or link_domain.lower() == base_domain.lower()
    except:
        return False

def should_download_file(link):
    """
    Check if a link points to a file type that should be downloaded.

    Args:
        link (str): The hyperlink URL.

    Returns:
        bool: True if the link ends with .pdf, .epub, or .html.
    """
    return link.lower().endswith(('.pdf', '.epub', '.html'))

def generate_unique_filename(url, ext):
    """
    Generate a consistent and unique filename for a URL using SHA-256 hashing.

    Args:
        url (str): The URL to hash.
        ext (str): The file extension (e.g., 'pdf', 'html').

    Returns:
        str: A unique filename in the format 'domain_hash.ext'.
    """
    # Create a short SHA-256 hash of the URL
    hash_digest = hashlib.sha256(url.encode()).hexdigest()[:10]
    
    # Replace dots in domain name with underscores for filesystem compatibility
    domain = urlparse(url).netloc.replace('.', '_')

    return f"{domain}_{hash_digest}.{ext}"
