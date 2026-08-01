import sys
import os
from unittest.mock import patch, MagicMock

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.ingestion.fundamentals.pipeline import FundamentalsPipeline, IngestionResult


class DummyCompany:
    def __init__(self, ticker="RELIANCE", company_id="1"):
        self.ticker = ticker
        self.id = company_id


@patch("app.ingestion.fundamentals.pipeline.FundamentalsService")
@patch("app.ingestion.fundamentals.pipeline.YahooFinanceProvider")
def test_pipeline_created(mock_provider_cls, mock_service):
    mock_service.needs_refresh.return_value = True
    mock_provider_instance = MagicMock()
    mock_provider_cls.return_value = mock_provider_instance
    mock_provider_instance.fetch.return_value = {
        "success": True,
        "data": {"current_price": 1000.0},
    }

    mock_service.ingest.return_value = (object(), True)

    result = FundamentalsPipeline.ingest_company(None, DummyCompany("RELIANCE", "1"))

    assert isinstance(result, IngestionResult)
    assert result.status == "created"
    assert result.ticker == "RELIANCE"


@patch("app.ingestion.fundamentals.pipeline.FundamentalsService")
def test_skip_if_recent(mock_service):
    mock_service.needs_refresh.return_value = False

    result = FundamentalsPipeline.ingest_company(None, DummyCompany("RELIANCE", "1"))

    assert isinstance(result, IngestionResult)
    assert result.status == "skipped"


@patch("app.ingestion.fundamentals.pipeline.FundamentalsService")
@patch("app.ingestion.fundamentals.pipeline.YahooFinanceProvider")
def test_provider_failure(mock_provider_cls, mock_service):
    mock_service.needs_refresh.return_value = True
    mock_provider_instance = MagicMock()
    mock_provider_cls.return_value = mock_provider_instance
    mock_provider_instance.fetch.return_value = {
        "success": False,
        "error": "Network Timeout Error",
    }

    result = FundamentalsPipeline.ingest_company(None, DummyCompany("RELIANCE", "1"))

    assert isinstance(result, IngestionResult)
    assert result.status == "failed"
    assert result.error == "Network Timeout Error"


@patch("app.ingestion.fundamentals.pipeline.CompanyService")
@patch("app.ingestion.fundamentals.pipeline.FundamentalsService")
@patch("app.ingestion.fundamentals.pipeline.YahooFinanceProvider")
def test_ingest_all_summary(mock_provider_cls, mock_service, mock_company_service):
    c1 = DummyCompany("RELIANCE", "1")
    c2 = DummyCompany("TCS", "2")
    c3 = DummyCompany("INFY", "3")
    mock_company_service.get_active_companies.return_value = [c1, c2, c3]

    # mock c1 -> created, c2 -> updated, c3 -> skipped
    mock_service.needs_refresh.side_effect = [True, True, False]
    mock_provider_instance = MagicMock()
    mock_provider_cls.return_value = mock_provider_instance
    mock_provider_instance.fetch.return_value = {"success": True, "data": {}}
    mock_service.ingest.side_effect = [(object(), True), (object(), False)]

    summary = FundamentalsPipeline.ingest_all(None)

    assert summary["processed"] == 3
    assert summary["created"] == 1
    assert summary["updated"] == 1
    assert summary["skipped"] == 1
    assert summary["failed"] == 0
    assert "duration_seconds" in summary
    assert summary["duration_seconds"] >= 0.0
