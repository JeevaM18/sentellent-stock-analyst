import os
import sys
import uuid
from unittest.mock import patch, MagicMock
import pytest  # pyrefly: ignore [missing-import]

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.db.database import SessionLocal
from app.constants.chunks import CHUNK_STATUS_EMBEDDED, CHUNK_STATUS_NEW, CHUNK_STATUS_FAILED
from app.embeddings.constants import EMBEDDING_DIMENSIONS
from app.embeddings.exceptions import EmbeddingProviderError
from app.embeddings.pipeline import EmbeddingPipeline
from app.embeddings.types import EmbeddingResult, EmbeddingPipelineSummary
from app.schemas.company import CompanyBase
from app.services.company_service import CompanyService
from app.services.news_service import NewsService
from app.services.chunk_service import ChunkService
from app.services.embedding_service import EmbeddingService


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_chunks(db):
    ticker = f"TEST_PIP_{uuid.uuid4().hex[:6].upper()}"
    company = CompanyService.create_company(
        db,
        CompanyBase(
            ticker=ticker,
            company_name=f"Test Pipeline Company {ticker}",
            exchange="NSE",
            sector="IT",
        ),
    )
    article = {
        "title": "Pipeline Analysis",
        "article_url": f"https://example.com/news/{uuid.uuid4().hex}",
        "content_hash": uuid.uuid4().hex,
        "summary": "Sample news text content. " * 30,
        "source": "Moneycontrol",
    }
    doc, _ = NewsService.ingest(db, company.id, article)
    chunks = ChunkService.chunk_document(db, document=doc)
    return chunks


def test_embed_chunk_created(db, sample_chunks):
    mock_provider = MagicMock()
    mock_provider.embed_text.return_value = EmbeddingResult(
        vector=[0.1] * EMBEDDING_DIMENSIONS, model="text-embedding-004", dimensions=768
    )

    pipeline = EmbeddingPipeline(provider=mock_provider)
    summary = pipeline.embed_chunk(db=db, chunk=sample_chunks[0])

    assert summary.processed == 1
    assert summary.created == 1
    assert summary.failed == 0
    mock_provider.embed_text.assert_called_once()


def test_embed_chunk_updated(db, sample_chunks):
    mock_provider = MagicMock()
    mock_provider.embed_text.return_value = EmbeddingResult(
        vector=[0.1] * EMBEDDING_DIMENSIONS, model="text-embedding-004", dimensions=768
    )

    pipeline = EmbeddingPipeline(provider=mock_provider)
    # First embed -> created
    pipeline.embed_chunk(db=db, chunk=sample_chunks[0])

    # Re-reset status to NEW for re-embedding test
    sample_chunks[0].status = CHUNK_STATUS_NEW
    db.commit()

    # Second embed -> updated
    summary = pipeline.embed_chunk(db=db, chunk=sample_chunks[0])
    assert summary.processed == 1
    assert summary.updated == 1


def test_provider_failure(db, sample_chunks):
    mock_provider = MagicMock()
    mock_provider.embed_text.side_effect = EmbeddingProviderError("API Quota Exceeded")

    pipeline = EmbeddingPipeline(provider=mock_provider)
    summary = pipeline.embed_chunk(db=db, chunk=sample_chunks[0])

    assert summary.processed == 1
    assert summary.failed == 1
    db.refresh(sample_chunks[0])
    assert sample_chunks[0].status == CHUNK_STATUS_FAILED


def test_embed_pending_empty(db):
    mock_provider = MagicMock()
    pipeline = EmbeddingPipeline(provider=mock_provider)

    with patch.object(EmbeddingService, "get_pending_chunks", return_value=[]):
        summary = pipeline.embed_pending(db=db)

    assert summary.processed == 0
    assert summary.created == 0
    assert summary.failed == 0
    mock_provider.embed_batch.assert_not_called()


def test_embed_pending_batch(db, sample_chunks):
    mock_provider = MagicMock()
    mock_provider.embed_batch.return_value = [
        EmbeddingResult(vector=[0.2] * EMBEDDING_DIMENSIONS) for _ in sample_chunks
    ]

    pipeline = EmbeddingPipeline(provider=mock_provider)
    summary = pipeline.embed_chunks(db=db, chunks=sample_chunks)

    assert summary.processed == len(sample_chunks)
    assert summary.created == len(sample_chunks)
    assert summary.failed == 0


def test_bulk_ingest_called_once(db, sample_chunks):
    mock_provider = MagicMock()
    mock_provider.embed_batch.return_value = [
        EmbeddingResult(vector=[0.3] * EMBEDDING_DIMENSIONS) for _ in sample_chunks
    ]

    pipeline = EmbeddingPipeline(provider=mock_provider)
    with patch.object(EmbeddingService, "bulk_ingest", wraps=EmbeddingService.bulk_ingest) as mock_bulk:
        pipeline.embed_chunks(db=db, chunks=sample_chunks)
        mock_bulk.assert_called_once()


def test_skip_already_embedded_chunk(db, sample_chunks):
    mock_provider = MagicMock()
    pipeline = EmbeddingPipeline(provider=mock_provider)

    # Mark chunk as EMBEDDED
    sample_chunks[0].status = CHUNK_STATUS_EMBEDDED
    db.commit()

    summary = pipeline.embed_chunk(db=db, chunk=sample_chunks[0])
    assert summary.processed == 0
    assert summary.created == 0
    mock_provider.embed_text.assert_not_called()
