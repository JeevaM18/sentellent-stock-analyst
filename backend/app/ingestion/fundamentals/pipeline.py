from dataclasses import dataclass
import logging
import time
from typing import Any
from sqlalchemy.orm import Session

from app.models.company import Company
from app.services.company_service import CompanyService
from app.services.fundamentals_service import FundamentalsService
from app.ingestion.fundamentals.provider import YahooFinanceProvider

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    ticker: str
    status: str  # "created", "updated", "skipped", "failed"
    error: str | None = None


class FundamentalsPipeline:

    @staticmethod
    def ingest_company(
        db: Session,
        company: Company,
    ) -> IngestionResult:
        """Fetch and ingest financial fundamentals for a single company if refresh is required."""
        if not FundamentalsService.needs_refresh(db, company.id):
            logger.info("Skipping %s (fundamentals are up to date)", company.ticker)
            return IngestionResult(ticker=company.ticker, status="skipped")

        payload = YahooFinanceProvider().fetch(company.ticker)

        if not payload.get("success"):
            error_msg = payload.get("error", "Unknown provider error")
            logger.error("Failed %s: %s", company.ticker, error_msg)
            return IngestionResult(
                ticker=company.ticker, status="failed", error=error_msg
            )

        try:
            _, created = FundamentalsService.ingest(
                db=db,
                company_id=company.id,
                payload=payload,
            )
            status_str = "created" if created else "updated"
            logger.info("Successfully %s fundamentals for %s", status_str, company.ticker)
            return IngestionResult(ticker=company.ticker, status=status_str)
        except Exception as e:
            logger.error("Failed to ingest %s: %s", company.ticker, str(e))
            return IngestionResult(ticker=company.ticker, status="failed", error=str(e))

    @staticmethod
    def ingest_companies(
        db: Session,
        companies: list[Company],
    ) -> dict[str, Any]:
        """Ingest fundamentals for a list of companies with performance timing."""
        start_time = time.perf_counter()
        summary = {
            "processed": 0,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "failed": 0,
            "duration_seconds": 0.0,
        }

        total = len(companies)
        logger.info("Beginning fundamentals ingestion for %d companies", total)

        for index, company in enumerate(companies, start=1):
            logger.info("[%d/%d] Ingesting %s", index, total, company.ticker)
            result = FundamentalsPipeline.ingest_company(db, company)

            summary["processed"] += 1
            if result.status in summary:
                summary[result.status] += 1
            else:
                summary["failed"] += 1

        elapsed = time.perf_counter() - start_time
        summary["duration_seconds"] = round(elapsed, 2)
        logger.info(
            "Completed ingestion in %.2fs. Processed: %d, Created: %d, Updated: %d, Skipped: %d, Failed: %d",
            elapsed,
            summary["processed"],
            summary["created"],
            summary["updated"],
            summary["skipped"],
            summary["failed"],
        )
        return summary

    @staticmethod
    def ingest_all(db: Session) -> dict[str, Any]:
        """Fetch all active listed companies and run fundamentals pipeline."""
        companies = CompanyService.get_active_companies(db)
        return FundamentalsPipeline.ingest_companies(db, companies)
