"""
Constants used throughout the Doudesu library.

This module contains all constant values used by the Doujindesu API wrapper,
including URLs, HTTP headers, and other configuration values.
"""

# Base URL for the doujindesu website
BASE_URL = "https://doujindesu.tv"

# API endpoint for chapter data
CHAPTER_API_ENDPOINT = f"{BASE_URL}/themes/ajax/ch.php"

# HTTP Headers
HEADERS = {
    "Referer": BASE_URL,
    "X-Requested-With": "XMLHttpRequest",
}

# TLS Client configuration
TLS_CLIENT_CONFIG = {
    "client_identifier": "chrome_120",
    "random_tls_extension_order": True,
}

# Regular expressions
CHAPTER_ID_PATTERN = r"load_data\((\d+)\)"
IMAGE_SRC_PATTERN = r"src=\"(.*?)\""

DEFAULT_SETTINGS = {
    "result_path": "result",
    "default_theme": "dark",
    "blur_thumbnails": True,
}
