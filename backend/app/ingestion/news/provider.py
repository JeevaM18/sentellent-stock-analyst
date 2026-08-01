from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

import feedparser
import requests

from app.ingestion.news.constants import (
    DEFAULT_COUNTRY,
    DEFAULT_LANGUAGE,
    GOOGLE_NEWS_RSS,
    MAX_ARTICLES_PER_COMPANY,
    REQUEST_TIMEOUT,
    USER_AGENT,
)
from app.ingestion.news.utils import (
    clean_summary,
    hash_url,
    normalize_url,
    parse_datetime,
)


class BaseNewsProvider(ABC):
    """Abstract base class for news providers."""

    @abstractmethod
    def fetch(self, company_or_name: Any, ticker: str | None = None) -> dict[str, Any]:
        """Fetch news articles for a specific company or company_name + ticker pair."""
        pass


class GoogleNewsRSSProvider(BaseNewsProvider):
    """
    Fetches news articles from Google News RSS feed, cleans HTML markup,
    normalizes URLs, generates content hashes, and sorts articles newest-first.
    """

    def fetch(self, company_or_name: Any, ticker: str | None = None) -> dict[str, Any]:
        # Support passing a Company object or separate company_name + ticker strings
        if hasattr(company_or_name, "company_name") and hasattr(company_or_name, "ticker"):
            company_name = company_or_name.company_name
            clean_ticker = company_or_name.ticker.strip().upper()
        else:
            company_name = str(company_or_name)
            clean_ticker = str(ticker).strip().upper() if ticker else ""

        query = f"{company_name} OR {clean_ticker}"

        try:
            response = requests.get(
                GOOGLE_NEWS_RSS,
                params={
                    "q": query,
                    "hl": DEFAULT_LANGUAGE,
                    "gl": DEFAULT_COUNTRY,
                    "ceid": f"{DEFAULT_COUNTRY}:{DEFAULT_LANGUAGE}",
                },
                headers={"User-Agent": USER_AGENT},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            feed = feedparser.parse(response.content)
            articles = []

            for entry in feed.entries[:MAX_ARTICLES_PER_COMPANY]:
                raw_url = entry.get("link", "")
                normalized_article_url = normalize_url(raw_url)
                title = entry.get("title", "").strip()

                published_dt = parse_datetime(entry.get("published"))

                source_val = "Google News"
                if isinstance(entry.get("source"), dict):
                    source_val = entry.get("source", {}).get("title", "Google News")

                articles.append(
                    {
                        "title": title,
                        "article_url": normalized_article_url,
                        "content_hash": hash_url(raw_url),
                        "summary": clean_summary(entry.get("summary"), title),
                        "published_at": published_dt,
                        "source": source_val,
                        "ticker": clean_ticker,
                        "company_name": company_name,
                        "language": DEFAULT_LANGUAGE,
                    }
                )

            # Sort articles newest first
            articles.sort(
                key=lambda x: x["published_at"] if x["published_at"] else datetime.min.replace(tzinfo=timezone.utc),
                reverse=True,
            )

            return {
                "success": True,
                "provider": "Google News RSS",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "company": company_name,
                "ticker": clean_ticker,
                "articles": articles,
            }

        except Exception as exc:
            return {
                "success": False,
                "provider": "Google News RSS",
                "ticker": clean_ticker,
                "error": str(exc),
                "articles": [],
            }
