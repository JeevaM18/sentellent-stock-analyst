from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
from urllib.parse import urlsplit
from bs4 import BeautifulSoup


def normalize_url(url: str) -> str:
    """Strip query parameters from URL for clean deduplication."""
    if not url:
        return ""
    return urlsplit(url)._replace(query="", fragment="").geturl()


def hash_url(url: str) -> str:
    """Generate SHA256 content hash of normalized URL."""
    clean = normalize_url(url)
    return hashlib.sha256(clean.encode("utf-8")).hexdigest()


def parse_datetime(published_str: str | None) -> datetime | None:
    """Parse RSS published date string into timezone-aware datetime."""
    if not published_str:
        return None
    try:
        dt = parsedate_to_datetime(published_str)
        if dt and dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def clean_summary(summary: str | None, fallback_title: str) -> str:
    """Clean HTML markup from RSS summary and fallback to title if empty."""
    if not summary:
        return fallback_title.strip()
    soup = BeautifulSoup(summary, "html.parser")
    text = soup.get_text(" ", strip=True)
    return text if text else fallback_title.strip()
