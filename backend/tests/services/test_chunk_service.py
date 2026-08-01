import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import hashlib
import uuid
import pytest  # pyrefly: ignore [missing-import]
from sqlalchemy.exc import IntegrityError

from app.db.database import SessionLocal
from app.constants.chunks import CHUNK_STATUS_NEW
from app.schemas.company import CompanyBase
from app.services.company_service import CompanyService
from app.services.news_service import NewsService
from app.services.chunk_service import ChunkService


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_document(db):
    ticker = f"TEST_CHK_{uuid.uuid4().hex[:6].upper()}"
    company = CompanyService.create_company(
        db,
        CompanyBase(
            ticker=ticker,
            company_name=f"Test Chunking Company {ticker}",
            exchange="NSE",
            sector="IT",
        ),
    )
    article = {
        "title": "Quarterly Financial Analysis",
        "article_url": f"https://example.com/news/{uuid.uuid4().hex}",
        "content_hash": uuid.uuid4().hex,
        "summary": "Full text analysis content of stock earnings report.",
        "source": "Moneycontrol",
    }
    doc, _ = NewsService.ingest(db, company.id, article)
    return doc


def test_create_chunk(db, sample_document):
    content = "Reliance Industries reported record Q1 revenue growth."
    c_hash = hashlib.sha256(content.encode()).hexdigest()

    chunk = ChunkService.create_chunk(
        db,
        document_id=sample_document.id,
        chunk_index=0,
        content=content,
        chunk_hash=c_hash,
        token_count=10,
        character_count=len(content),
        start_char=0,
        end_char=len(content),
        status=CHUNK_STATUS_NEW,
    )

    assert chunk.id is not None
    assert chunk.document_id == sample_document.id
    assert chunk.chunk_index == 0
    assert chunk.content == content
    assert chunk.chunk_hash == c_hash
    assert chunk.token_count == 10
    assert chunk.character_count == len(content)
    assert chunk.start_char == 0
    assert chunk.end_char == len(content)
    assert chunk.status == CHUNK_STATUS_NEW


def test_get_chunks_ordering(db, sample_document):
    # Create chunks out of index order
    c2 = "Chunk 2 content text"
    c1 = "Chunk 1 content text"
    c0 = "Chunk 0 content text"

    ChunkService.create_chunk(
        db,
        document_id=sample_document.id,
        chunk_index=2,
        content=c2,
        chunk_hash=hashlib.sha256(c2.encode()).hexdigest(),
        token_count=4,
        character_count=len(c2),
    )
    ChunkService.create_chunk(
        db,
        document_id=sample_document.id,
        chunk_index=0,
        content=c0,
        chunk_hash=hashlib.sha256(c0.encode()).hexdigest(),
        token_count=4,
        character_count=len(c0),
    )
    ChunkService.create_chunk(
        db,
        document_id=sample_document.id,
        chunk_index=1,
        content=c1,
        chunk_hash=hashlib.sha256(c1.encode()).hexdigest(),
        token_count=4,
        character_count=len(c1),
    )

    chunks = ChunkService.get_chunks(db, sample_document.id)
    assert len(chunks) == 3
    assert [c.chunk_index for c in chunks] == [0, 1, 2]
    assert chunks[0].content == c0
    assert chunks[1].content == c1
    assert chunks[2].content == c2


def test_replace_chunks(db, sample_document):
    # Initial 2 chunks
    initial = [
        {"chunk_index": 0, "content": "Old C0", "chunk_hash": "h0", "token_count": 2, "character_count": 6},
        {"chunk_index": 1, "content": "Old C1", "chunk_hash": "h1", "token_count": 2, "character_count": 6},
    ]
    ChunkService.replace_chunks(db, document_id=sample_document.id, chunks_data=initial)
    assert len(ChunkService.get_chunks(db, sample_document.id)) == 2

    # Replace with 3 new chunks
    replacement = [
        {"chunk_index": 0, "content": "New C0", "chunk_hash": "nh0", "token_count": 3, "character_count": 6},
        {"chunk_index": 1, "content": "New C1", "chunk_hash": "nh1", "token_count": 3, "character_count": 6},
        {"chunk_index": 2, "content": "New C2", "chunk_hash": "nh2", "token_count": 3, "character_count": 6},
    ]
    new_chunks = ChunkService.replace_chunks(db, document_id=sample_document.id, chunks_data=replacement)
    assert len(new_chunks) == 3

    fetched = ChunkService.get_chunks(db, sample_document.id)
    assert len(fetched) == 3
    assert fetched[0].content == "New C0"
    assert fetched[2].content == "New C2"


def test_unique_constraint_conflict(db, sample_document):
    c0 = "First chunk"
    ChunkService.create_chunk(
        db,
        document_id=sample_document.id,
        chunk_index=0,
        content=c0,
        chunk_hash="h0",
        token_count=2,
        character_count=len(c0),
    )

    with pytest.raises(IntegrityError):
        ChunkService.create_chunk(
            db,
            document_id=sample_document.id,
            chunk_index=0,  # Duplicate chunk_index 0
            content="Duplicate chunk",
            chunk_hash="h_dup",
            token_count=2,
            character_count=15,
        )
    db.rollback()


def test_cascade_delete(db, sample_document):
    c0 = "Cascade chunk"
    ChunkService.create_chunk(
        db,
        document_id=sample_document.id,
        chunk_index=0,
        content=c0,
        chunk_hash="h0",
        token_count=2,
        character_count=len(c0),
    )

    doc_id = sample_document.id
    db.delete(sample_document)
    db.commit()

    assert len(ChunkService.get_chunks(db, doc_id)) == 0
