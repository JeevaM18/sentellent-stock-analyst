import sys
import os
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
import pytest  # pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.main import app
from app.db.database import SessionLocal
from app.embeddings.constants import EMBEDDING_DIMENSIONS
from app.embeddings.types import EmbeddingResult
from app.retrieval.constants import DEFAULT_MIN_SIMILARITY
from app.retrieval.service import RetrieverService
from app.retrieval.utils import clamp_top_k, validate_query
from app.schemas.company import CompanyBase
from app.services.company_service import CompanyService
from app.services.news_service import NewsService
from app.services.chunk_service import ChunkService
from app.services.embedding_service import EmbeddingService

client = TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_indexed_company(db):
    ticker = f"TEST_RET_{uuid.uuid4().hex[:6].upper()}"
    company = CompanyService.create_company(
        db,
        CompanyBase(
            ticker=ticker,
            company_name=f"Test Retrieval Company {ticker}",
            exchange="NSE",
            sector="IT",
        ),
    )

    now = datetime.now(timezone.utc)
    doc_data = {
        "title": "Reliance Q1 Financial Performance Overview",
        "article_url": f"https://example.com/news/{uuid.uuid4().hex}",
        "content_hash": uuid.uuid4().hex,
        "summary": "Reliance Industries reported strong quarter revenue growth in energy and retail.",
        "source": "Moneycontrol",
        "published_at": now - timedelta(days=2),
    }

    doc, _ = NewsService.ingest(db, company.id, doc_data)
    chunks = ChunkService.chunk_document(db, document=doc)

    res = EmbeddingResult(vector=[0.1] * EMBEDDING_DIMENSIONS, model="gemini-embedding-001")
    EmbeddingService.ingest(db, chunk_id=chunks[0].id, embedding_result=res)

    return company, doc, chunks[0]


def test_empty_query():
    with pytest.raises(ValueError, match="Search query cannot be empty"):
        validate_query("")

    with pytest.raises(ValueError, match="Search query cannot be empty"):
        validate_query("   ")


def test_top_k_limit():
    assert clamp_top_k(-5) == 1
    assert clamp_top_k(0) == 1
    assert clamp_top_k(5) == 5
    assert clamp_top_k(100) == 20


@patch("app.retrieval.service.GoogleEmbeddingProvider")
def test_retrieve_success(mock_provider_cls, db, sample_indexed_company):
    company, doc, chunk = sample_indexed_company

    mock_provider = MagicMock()
    mock_provider.embed_text.return_value = EmbeddingResult(vector=[0.1] * EMBEDDING_DIMENSIONS)
    mock_provider_cls.return_value = mock_provider

    service = RetrieverService(provider=mock_provider)
    summary = service.retrieve(db=db, query="Reliance Q1 earnings", top_k=5, min_similarity=0.50, ticker=company.ticker)

    assert summary.query == "Reliance Q1 earnings"
    assert summary.total >= 1
    assert summary.duration_seconds >= 0.0
    assert summary.results[0].chunk_id == chunk.id
    assert summary.results[0].ticker == company.ticker
    assert summary.results[0].similarity > 0.50


@patch("app.retrieval.service.GoogleEmbeddingProvider")
def test_retrieve_with_company_filter(mock_provider_cls, db, sample_indexed_company):
    company, doc, chunk = sample_indexed_company

    mock_provider = MagicMock()
    mock_provider.embed_text.return_value = EmbeddingResult(vector=[0.1] * EMBEDDING_DIMENSIONS)
    mock_provider_cls.return_value = mock_provider

    service = RetrieverService(provider=mock_provider)

    # Match by ticker
    res_ticker = service.retrieve(db=db, query="Reliance Q1", ticker=company.ticker, min_similarity=0.50)
    assert res_ticker.total >= 1
    assert res_ticker.results[0].company_id == company.id

    # Non-matching ticker filter
    res_no_match = service.retrieve(db=db, query="Reliance Q1", ticker="NONEXISTENT_TICKER", min_similarity=0.50)
    assert res_no_match.total == 0


@patch("app.retrieval.service.GoogleEmbeddingProvider")
def test_similarity_threshold(mock_provider_cls, db, sample_indexed_company):
    company, doc, chunk = sample_indexed_company

    mock_provider = MagicMock()
    # High orthogonal vector resulting in low similarity
    mock_provider.embed_text.return_value = EmbeddingResult(vector=[-0.9] * EMBEDDING_DIMENSIONS)
    mock_provider_cls.return_value = mock_provider

    service = RetrieverService(provider=mock_provider)

    # High similarity threshold (0.99) should filter out result
    summary = service.retrieve(db=db, query="Reliance Q1", min_similarity=0.99, ticker=company.ticker)
    assert summary.total == 0


@patch("app.retrieval.service.GoogleEmbeddingProvider")
def test_retrieval_api_endpoint(mock_provider_cls, db, sample_indexed_company):
    company, doc, chunk = sample_indexed_company

    mock_provider = MagicMock()
    mock_provider.embed_text.return_value = EmbeddingResult(vector=[0.1] * EMBEDDING_DIMENSIONS)
    mock_provider_cls.return_value = mock_provider

    with patch("app.api.retrieval.router.RetrieverService") as mock_svc_cls:
        mock_svc_cls.return_value.retrieve.return_value = RetrieverService(provider=mock_provider).retrieve(
            db=db, query="Reliance Q1 earnings", ticker=company.ticker, min_similarity=0.50
        )

        response = client.post(
            "/api/retrieval/search",
            json={
                "query": "Reliance Q1 earnings",
                "top_k": 5,
                "ticker": company.ticker,
                "min_similarity": 0.50,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "Reliance Q1 earnings"
        assert data["total"] >= 1
        assert "duration_ms" in data
        assert data["chunks"][0]["ticker"] == company.ticker
