import sys
import os
import uuid
from datetime import datetime, timedelta, timezone
import pytest

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.db.database import SessionLocal
from app.services.company_service import CompanyService
from app.services.fundamentals_service import FundamentalsService, current_utc


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_company(db):
    ticker = f"TEST_{uuid.uuid4().hex[:6].upper()}"
    from app.schemas.company import CompanyBase
    company = CompanyService.create_company(
        db,
        CompanyBase(
            ticker=ticker,
            company_name=f"Test Company {ticker}",
            exchange="NSE",
            sector="IT",
        ),
    )
    return company


def test_fundamentals_ingest_create_and_update(db, sample_company):
    sample_payload = {
        "success": True,
        "ticker": sample_company.ticker,
        "provider": "Yahoo Finance",
        "retrieved_at": current_utc().isoformat(),
        "data": {
            "current_price": 1500.50,
            "market_cap": 1000000000,
            "shares_outstanding": 500000,
            "pe_ratio": 25.4,
            "eps": 60.2,
            "roe": 0.18,
            "debt_to_equity": 12.5,
            "dividend_yield": 1.2,
            "book_value": 300.0,
            "price_to_book": 5.0,
            "beta": 0.8,
            "fifty_two_week_high": 1600.0,
            "fifty_two_week_low": 1200.0,
            "currency": "INR",
        },
    }

    # 1. Initial Ingest -> Created (created = True)
    fundamentals, created = FundamentalsService.ingest(db, sample_company.id, sample_payload)
    assert created is True
    assert fundamentals.company_id == sample_company.id
    assert float(fundamentals.current_price) == 1500.50
    assert fundamentals.market_cap == 1000000000
    assert float(fundamentals.pe_ratio) == 25.4
    assert fundamentals.currency == "INR"

    # 2. Re-ingest with updated price -> Updated (created = False)
    sample_payload["data"]["current_price"] = 1550.75
    sample_payload["data"]["pe_ratio"] = 26.1

    updated_fundamentals, updated_created = FundamentalsService.ingest(
        db, sample_company.id, sample_payload
    )
    assert updated_created is False
    assert updated_fundamentals.id == fundamentals.id
    assert float(updated_fundamentals.current_price) == 1550.75
    assert float(updated_fundamentals.pe_ratio) == 26.1


def test_needs_refresh(db, sample_company):
    # 1. Non-existent -> needs_refresh is True
    assert FundamentalsService.needs_refresh(db, sample_company.id) is True

    # 2. Fresh record -> needs_refresh is False
    payload = {
        "current_price": 100.0,
        "currency": "INR",
    }
    FundamentalsService.ingest(db, sample_company.id, payload)
    assert FundamentalsService.needs_refresh(db, sample_company.id, max_age_hours=24) is False

    # 3. Artificially age timestamp past 24 hours -> needs_refresh is True
    fundamentals = FundamentalsService.get_by_company(db, sample_company.id)
    fundamentals.last_updated = current_utc() - timedelta(hours=25)
    db.commit()

    assert FundamentalsService.needs_refresh(db, sample_company.id, max_age_hours=24) is True


def test_bulk_ingest(db):
    from app.schemas.company import CompanyBase
    c1 = CompanyService.create_company(db, CompanyBase(ticker=f"B1_{uuid.uuid4().hex[:4]}", company_name="Bulk 1", exchange="NSE"))
    c2 = CompanyService.create_company(db, CompanyBase(ticker=f"B2_{uuid.uuid4().hex[:4]}", company_name="Bulk 2", exchange="NSE"))

    items = [
        (c1.id, {"current_price": 100.0, "currency": "INR"}),
        (c2.id, {"current_price": 200.0, "currency": "INR"}),
    ]

    created_count, updated_count = FundamentalsService.bulk_ingest(db, items)
    assert created_count == 2
    assert updated_count == 0


def test_invalid_payload_rejection(db, sample_company):
    invalid_payload = {
        "success": False,
        "error": "Symbol not found",
    }
    with pytest.raises(ValueError, match="Cannot ingest invalid provider payload"):
        FundamentalsService.ingest(db, sample_company.id, invalid_payload)
