import sys
import os
import uuid
from unittest.mock import patch, MagicMock

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.ingestion.news.pipeline import NewsPipeline, CompanyIngestionResult, PipelineSummary


class DummyCompany:
    def __init__(self, company_name="Reliance Industries", ticker="RELIANCE", company_id="1"):
        self.company_name = company_name
        self.ticker = ticker
        self.id = company_id


@patch("app.ingestion.news.pipeline.GoogleNewsRSSProvider")
@patch("app.ingestion.news.pipeline.NewsService")
def test_pipeline_company_success(mock_service, mock_provider_cls):
    mock_provider_instance = MagicMock()
    mock_provider_cls.return_value = mock_provider_instance
    mock_provider_instance.fetch.return_value = {
        "success": True,
        "articles": [
            {"title": "Article 1", "article_url": "https://news.com/1"},
            {"title": "Article 2", "article_url": "https://news.com/2"},
        ],
    }
    mock_service.bulk_ingest.return_value = {
        "created": 2,
        "updated": 0,
        "duplicates": 0,
        "failed": 0,
    }

    res = NewsPipeline.ingest_company(None, DummyCompany("Reliance Industries", "RELIANCE"))

    assert isinstance(res, CompanyIngestionResult)
    assert res.ticker == "RELIANCE"
    assert res.processed == 2
    assert res.created == 2
    assert res.failed == 0


@patch("app.ingestion.news.pipeline.GoogleNewsRSSProvider")
def test_pipeline_provider_failure(mock_provider_cls):
    mock_provider_instance = MagicMock()
    mock_provider_cls.return_value = mock_provider_instance
    mock_provider_instance.fetch.return_value = {
        "success": False,
        "error": "RSS Timeout",
        "articles": [],
    }

    res = NewsPipeline.ingest_company(None, DummyCompany("Reliance Industries", "RELIANCE"))

    assert isinstance(res, CompanyIngestionResult)
    assert res.ticker == "RELIANCE"
    assert res.failed == 1
    assert res.error == "RSS Timeout"


@patch("app.ingestion.news.pipeline.GoogleNewsRSSProvider")
def test_empty_feed_skipped(mock_provider_cls):
    mock_provider_instance = MagicMock()
    mock_provider_cls.return_value = mock_provider_instance
    mock_provider_instance.fetch.return_value = {
        "success": True,
        "articles": [],
    }

    res = NewsPipeline.ingest_company(None, DummyCompany("Reliance Industries", "RELIANCE"))

    assert isinstance(res, CompanyIngestionResult)
    assert res.ticker == "RELIANCE"
    assert res.skipped == 1
    assert res.failed == 0


@patch("app.ingestion.news.pipeline.WatchlistService")
@patch("app.ingestion.news.pipeline.GoogleNewsRSSProvider")
@patch("app.ingestion.news.pipeline.NewsService")
def test_ingest_watchlist(mock_news_service, mock_provider_cls, mock_watchlist_service):
    c1 = DummyCompany("Reliance Industries", "RELIANCE", "1")
    c2 = DummyCompany("Infosys", "INFY", "2")
    mock_watchlist_service.get_followed_companies.return_value = [c1, c2]

    mock_provider_instance = MagicMock()
    mock_provider_cls.return_value = mock_provider_instance
    mock_provider_instance.fetch.return_value = {
        "success": True,
        "articles": [{"title": "News 1"}],
    }
    mock_news_service.bulk_ingest.return_value = {"created": 1, "updated": 0, "duplicates": 0, "failed": 0}

    summary = NewsPipeline.ingest_watchlist(None, uuid.uuid4())

    assert isinstance(summary, PipelineSummary)
    assert summary.companies_processed == 2
    assert summary.articles_processed == 2
    assert summary.created == 2


@patch("app.ingestion.news.pipeline.GoogleNewsRSSProvider")
@patch("app.ingestion.news.pipeline.NewsService")
def test_mixed_pipeline_execution(mock_news_service, mock_provider_cls):
    cA = DummyCompany("Company A", "COMPA", "1")
    cB = DummyCompany("Company B", "COMPB", "2")
    cC = DummyCompany("Company C", "COMPC", "3")
    cD = DummyCompany("Company D", "COMPD", "4")

    mock_provider_instance = MagicMock()
    mock_provider_cls.return_value = mock_provider_instance

    # Mock side effects for A (Success), B (RSS Error), C (Empty Feed), D (Success)
    mock_provider_instance.fetch.side_effect = [
        {"success": True, "articles": [{"title": "A1"}]},
        {"success": False, "error": "Connection Failed", "articles": []},
        {"success": True, "articles": []},
        {"success": True, "articles": [{"title": "D1"}]},
    ]
    mock_news_service.bulk_ingest.side_effect = [
        {"created": 1, "updated": 0, "duplicates": 0, "failed": 0},
        {"created": 0, "updated": 1, "duplicates": 1, "failed": 0},
    ]

    summary = NewsPipeline.ingest_companies(None, [cA, cB, cC, cD])

    assert summary.companies_processed == 4
    assert summary.articles_processed == 2
    assert summary.created == 1
    assert summary.updated == 1
    assert summary.skipped == 1
    assert summary.failed == 1
    assert summary.duration_seconds >= 0.0
