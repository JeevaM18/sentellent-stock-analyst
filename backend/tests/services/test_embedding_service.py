import os
import sys
import uuid
from datetime import datetime, timezone
import pytest  # pyrefly: ignore [missing-import]

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.db.database import SessionLocal
from app.constants.chunks import CHUNK_STATUS_EMBEDDED, CHUNK_STATUS_NEW
from app.embeddings.constants import EMBEDDING_DIMENSIONS
from app.embeddings.types import EmbeddingJob, EmbeddingResult
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
def sample_chunk(db):
    ticker = f"TEST_EMB_{uuid.uuid4().hex[:6].upper()}"
    company = CompanyService.create_company(
        db,
        CompanyBase(
            ticker=ticker,
            company_name=f"Test Embedding Company {ticker}",
            exchange="NSE",
            sector="IT",
        ),
    )
    article = {
        "title": "Quarterly Results",
        "article_url": f"https://example.com/news/{uuid.uuid4().hex}",
        "content_hash": uuid.uuid4().hex,
        "summary": "Sample news summary content.",
        "source": "Moneycontrol",
    }
    doc, _ = NewsService.ingest(db, company.id, article)
    chunks = ChunkService.chunk_document(db, document=doc)
    return chunks[0]


def test_create_embedding(db, sample_chunk):
    res = EmbeddingResult(
        vector=[0.05] * EMBEDDING_DIMENSIONS,
        model="text-embedding-004",
        dimensions=768,
        provider="google",
    )

    record, created = EmbeddingService.ingest(db, chunk_id=sample_chunk.id, embedding_result=res)

    assert created is True
    assert record.chunk_id == sample_chunk.id
    assert record.provider == "google"
    assert record.embedding_model == "text-embedding-004"
    assert record.dimensions == 768
    assert len(record.embedding) == 768

    db.refresh(sample_chunk)
    assert sample_chunk.status == CHUNK_STATUS_EMBEDDED


def test_update_existing_embedding(db, sample_chunk):
    res1 = EmbeddingResult(vector=[0.1] * EMBEDDING_DIMENSIONS, model="text-embedding-004")
    rec1, created1 = EmbeddingService.ingest(db, chunk_id=sample_chunk.id, embedding_result=res1)
    assert created1 is True

    # Re-ingest with updated vector
    res2 = EmbeddingResult(vector=[0.2] * EMBEDDING_DIMENSIONS, model="text-embedding-004")
    rec2, created2 = EmbeddingService.ingest(db, chunk_id=sample_chunk.id, embedding_result=res2)

    assert created2 is False
    assert rec2.id == rec1.id
    assert abs(rec2.embedding[0] - 0.2) < 1e-6


def test_duplicate_chunk_upsert(db, sample_chunk):
    res = EmbeddingResult(vector=[0.3] * EMBEDDING_DIMENSIONS)
    rec1, created1 = EmbeddingService.ingest(db, chunk_id=sample_chunk.id, embedding_result=res)
    assert created1 is True

    rec2, created2 = EmbeddingService.ingest(db, chunk_id=sample_chunk.id, embedding_result=res)
    assert created2 is False
    assert rec2.id == rec1.id


def test_bulk_ingest(db, sample_chunk):
    res = EmbeddingResult(vector=[0.4] * EMBEDDING_DIMENSIONS)
    job = EmbeddingJob(chunk_id=sample_chunk.id, embedding=res)

    stats = EmbeddingService.bulk_ingest(db, [job])

    assert stats["created"] == 1
    assert stats["updated"] == 0
    assert stats["failed"] == 0
    assert EmbeddingService.exists(db, sample_chunk.id) is True


def test_delete_embedding(db, sample_chunk):
    res = EmbeddingResult(vector=[0.5] * EMBEDDING_DIMENSIONS)
    EmbeddingService.ingest(db, chunk_id=sample_chunk.id, embedding_result=res)

    assert EmbeddingService.exists(db, sample_chunk.id) is True
    deleted = EmbeddingService.delete(db, sample_chunk.id)
    assert deleted == 1
    assert EmbeddingService.exists(db, sample_chunk.id) is False


def test_get_pending_chunks(db, sample_chunk):
    pending = EmbeddingService.get_pending_chunks(db, limit=1000)
    assert len(pending) >= 1
    assert any(c.id == sample_chunk.id for c in pending)


def test_transaction_rollback(db, sample_chunk):
    invalid_res = EmbeddingResult(vector=[0.1] * 100)  # Invalid 100 dimensions

    with pytest.raises(ValueError, match="Expected 768 dimensions but got 100"):
        EmbeddingService.ingest(db, chunk_id=sample_chunk.id, embedding_result=invalid_res)

    assert EmbeddingService.exists(db, sample_chunk.id) is False
