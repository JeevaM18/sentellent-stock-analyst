from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.company_fundamentals import CompanyFundamentals


def current_utc() -> datetime:
    """Helper function to return current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class BaseIngestionService(ABC):
    """Abstract base class for all data ingestion services."""

    @abstractmethod
    def ingest(self, db: Session, *args: Any, **kwargs: Any) -> Any:
        pass


class FundamentalsService(BaseIngestionService):

    @staticmethod
    def get_by_company(db: Session, company_id: UUID) -> CompanyFundamentals | None:
        """Retrieve latest fundamentals record for a given company."""
        return (
            db.query(CompanyFundamentals)
            .filter(CompanyFundamentals.company_id == company_id)
            .first()
        )

    @staticmethod
    def needs_refresh(db: Session, company_id: UUID, max_age_hours: int = 24) -> bool:
        """Check if company fundamentals record is missing or older than max_age_hours."""
        fundamentals = FundamentalsService.get_by_company(db, company_id)
        if not fundamentals or not fundamentals.last_updated:
            return True

        age = current_utc() - fundamentals.last_updated
        return age > timedelta(hours=max_age_hours)

    @staticmethod
    def ingest(
        db: Session, company_id: UUID, payload: dict[str, Any]
    ) -> tuple[CompanyFundamentals, bool]:
        """
        UPSERT fundamentals data into PostgreSQL.
        Returns tuple of (CompanyFundamentals, created: bool).
        """
        # Unwrap provider metadata envelope if present
        data = payload.get("data", payload)
        if isinstance(payload, dict) and "success" in payload:
            if not payload["success"]:
                raise ValueError(
                    f"Cannot ingest invalid provider payload: {payload.get('error', 'Unknown error')}"
                )

        if not isinstance(data, dict):
            raise ValueError("Payload data must be a valid dictionary")

        try:
            fundamentals = FundamentalsService.get_by_company(db, company_id)
            created = False

            if not fundamentals:
                fundamentals = CompanyFundamentals(company_id=company_id)
                db.add(fundamentals)
                created = True

            # Update fields
            for field in [
                "current_price",
                "market_cap",
                "shares_outstanding",
                "pe_ratio",
                "eps",
                "roe",
                "debt_to_equity",
                "dividend_yield",
                "book_value",
                "price_to_book",
                "beta",
                "fifty_two_week_high",
                "fifty_two_week_low",
            ]:
                if field in data and data[field] is not None:
                    setattr(fundamentals, field, data[field])

            if "currency" in data and data["currency"]:
                fundamentals.currency = data["currency"]

            fundamentals.last_updated = current_utc()

            db.commit()
            db.refresh(fundamentals)
            return fundamentals, created

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def bulk_ingest(
        db: Session, items: list[tuple[UUID, dict[str, Any]]]
    ) -> tuple[int, int]:
        """
        Bulk UPSERT fundamentals for multiple companies in a single transaction.
        Returns tuple of (created_count, updated_count).
        """
        created_count = 0
        updated_count = 0

        try:
            for company_id, payload in items:
                _, created = FundamentalsService.ingest(db, company_id, payload)
                if created:
                    created_count += 1
                else:
                    updated_count += 1

            return created_count, updated_count
        except Exception as e:
            db.rollback()
            raise e
