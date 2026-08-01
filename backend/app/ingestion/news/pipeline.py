from dataclasses import dataclass
import logging
import time
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.company import Company
from app.services.company_service import CompanyService
from app.services.watchlist_service import WatchlistService
from app.ingestion.news.provider import GoogleNewsRSSProvider

logger = logging.getLogger(__name__)


@dataclass
class CompanyIngestionResult:
    ticker: str
    processed: int
    created: int
    updated: int
    duplicates: int
    skipped: int
    failed: int
    error: str | None = None


@dataclass
class PipelineSummary:
    companies_processed: int
    articles_processed: int
    created: int
    updated: int
    duplicates: int
    skipped: int
    failed: int
    duration_seconds: float


class NewsPipeline:

    @staticmethod
    def ingest_company(
        db: Session,
        company: Company,
    ) -> CompanyIngestionResult:
        """Fetch and ingest news articles for a single company."""
        from app.services.news_service import NewsService

        provider = GoogleNewsRSSProvider()
        payload = provider.fetch(company)

        if not payload.get("success"):
            error_msg = payload.get("error", "Unknown RSS provider error")
            logger.error("Failed fetching news RSS for %s: %s", company.ticker, error_msg)
            return CompanyIngestionResult(
                ticker=company.ticker,
                processed=0,
                created=0,
                updated=0,
                duplicates=0,
                skipped=0,
                failed=1,
                error=error_msg,
            )

        articles = payload.get("articles", [])
        if not articles:
            logger.info("Skipped %s (0 recent news articles found)", company.ticker)
            return CompanyIngestionResult(
                ticker=company.ticker,
                processed=0,
                created=0,
                updated=0,
                duplicates=0,
                skipped=1,
                failed=0,
            )

        stats = NewsService.bulk_ingest(db, company.id, articles)
        logger.info(
            "%s - Fetched: %d, Created: %d, Updated: %d, Duplicates: %d, Failed: %d",
            company.ticker,
            len(articles),
            stats["created"],
            stats["updated"],
            stats["duplicates"],
            stats["failed"],
        )

        return CompanyIngestionResult(
            ticker=company.ticker,
            processed=len(articles),
            created=stats["created"],
            updated=stats["updated"],
            duplicates=stats["duplicates"],
            skipped=0,
            failed=stats["failed"],
        )

    @staticmethod
    def ingest_companies(
        db: Session,
        companies: list[Company],
    ) -> PipelineSummary:
        """Batch ingest news articles across a list of companies with timing statistics."""
        start_time = time.perf_counter()
        total_companies = len(companies)
        logger.info("Beginning news ingestion pipeline for %d companies", total_companies)

        articles_processed = 0
        total_created = 0
        total_updated = 0
        total_duplicates = 0
        total_skipped = 0
        total_failed = 0

        for index, company in enumerate(companies, start=1):
            logger.info("[%d/%d] Ingesting news for %s", index, total_companies, company.ticker)
            res = NewsPipeline.ingest_company(db, company)

            articles_processed += res.processed
            total_created += res.created
            total_updated += res.updated
            total_duplicates += res.duplicates
            total_skipped += res.skipped
            total_failed += res.failed

        elapsed = round(time.perf_counter() - start_time, 2)
        summary = PipelineSummary(
            companies_processed=total_companies,
            articles_processed=articles_processed,
            created=total_created,
            updated=total_updated,
            duplicates=total_duplicates,
            skipped=total_skipped,
            failed=total_failed,
            duration_seconds=elapsed,
        )

        logger.info(
            "Completed news ingestion pipeline in %.2fs. Companies: %d, Articles: %d (Created: %d, Updated: %d, Duplicates: %d, Skipped: %d, Failed: %d)",
            elapsed,
            total_companies,
            articles_processed,
            total_created,
            total_updated,
            total_duplicates,
            total_skipped,
            total_failed,
        )
        return summary

    @staticmethod
    def ingest_all(db: Session) -> PipelineSummary:
        """Ingest news articles for all active listed companies."""
        companies = CompanyService.get_active_companies(db)
        return NewsPipeline.ingest_companies(db, companies)

    @staticmethod
    def ingest_watchlist(db: Session, user_id: UUID) -> PipelineSummary:
        """Ingest news articles specifically for companies followed by a given user."""
        companies = WatchlistService.get_followed_companies(db, user_id)
        return NewsPipeline.ingest_companies(db, companies)
