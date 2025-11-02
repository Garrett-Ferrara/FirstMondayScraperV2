"""
Configuration settings for First Monday scraper
"""

# Base URLs
BASE_URL = "https://firstmonday.org"
ARCHIVE_URL = f"{BASE_URL}/ojs/index.php/fm/issue/archive"
OJS_ARTICLE_BASE = f"{BASE_URL}/ojs/index.php/fm/article/view"
LEGACY_BASE = f"{BASE_URL}/issues"

# Crawling settings
REQUEST_DELAY = 2.5  # seconds between requests
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# User agent (identify as academic research bot)
USER_AGENT = "FirstMondayResearchBot/1.0 (Academic Research; Contact: your-email@example.com)"

# Headers
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Output settings
OUTPUT_DIR = "data"
ISSUES_DIR = f"{OUTPUT_DIR}/issues"  # Organized by issue
METADATA_DIR = f"{OUTPUT_DIR}/metadata"  # Flat metadata (legacy)
FULLTEXT_DIR = f"{OUTPUT_DIR}/fulltext"  # Flat fulltext (legacy)
CHECKPOINT_FILE = f"{OUTPUT_DIR}/checkpoint.json"
LOG_FILE = f"{OUTPUT_DIR}/scraper.log"

# Organization settings
ORGANIZE_BY_ISSUE = True  # When True, organize files by issue folders

# Data extraction settings
EXTRACT_FULL_TEXT = True
EXTRACT_PDF = False  # Set to True to also download PDFs
MAX_ARTICLES_PER_RUN = None  # Set to a number for testing (e.g., 10)
