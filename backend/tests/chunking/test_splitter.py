import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import uuid
import pytest  # pyrefly: ignore [missing-import]

from app.db.database import SessionLocal
from app.chunking import DocumentChunker, ChunkData
from app.services.company_service import CompanyService
from app.services.news_service import NewsService
from app.services.chunk_service import ChunkService
from app.schemas.company import CompanyBase


def test_split_long_document():
    chunker = DocumentChunker(strategy="recursive")
    text = "Reliance Industries Q1 growth performance analysis. " * 300
    chunks = chunker.split_text(text)

    assert isinstance(chunks, list)
    assert len(chunks) > 1
    assert all(isinstance(c, ChunkData) for c in chunks)
    assert chunks[0].character_count > 0
    assert chunks[0].token_count > 0


def test_small_document():
    chunker = DocumentChunker(strategy="recursive")
    chunks = chunker.split_text("Small stock news update.")

    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].content == "Small stock news update."


def test_empty_document():
    chunker = DocumentChunker(strategy="recursive")
    chunks = chunker.split_text("")
    assert chunks == []

    chunks_space = chunker.split_text("   ")
    assert chunks_space == []


def test_chunk_indexes():
    chunker = DocumentChunker(strategy="recursive")
    text = "".join([f"Tata Consultancy Services contract expansion #{i}.\n\n" for i in range(100)])
    chunks = chunker.split_text(text)

    indexes = [c.chunk_index for c in chunks]
    assert indexes == list(range(len(chunks)))


def test_hash_uniqueness():
    chunker = DocumentChunker(strategy="recursive")
    text = "".join([f"Infosys AI investment announcement update #{i}.\n\n" for i in range(100)])
    chunks = chunker.split_text(text)

    hashes = {c.chunk_hash for c in chunks}
    assert len(hashes) == len(chunks)


def test_unicode_chunking():
    chunker = DocumentChunker(strategy="recursive")
    multilingual_text = (
        "Reliance Industries news update in multiple languages:\n\n"
        "English: Reliance launched new renewable energy projects in Gujarat.\n"
        "தமிழ்: ரிலையன்ஸ் நிறுவனம் புதிய புதுப்பிக்கத்தக்க எரிசக்தி திட்டங்களை தொடங்கியது.\n"
        "हिन्दी: रिलायंस इंडस्ट्रीज ने गुजरात में नई नवीकरणीय ऊर्जा परियोजनाओं की शुरुआत की।"
    )

    chunks = chunker.split_text(multilingual_text, document_title="Multilingual News", company_id="test-uuid")

    assert len(chunks) >= 1
    assert chunks[0].token_count > 0
    assert chunks[0].character_count == len(multilingual_text)
    assert "தமிழ்" in chunks[0].content
    assert "हिन्दी" in chunks[0].content


def test_chunk_document_service_integration():
    db = SessionLocal()
    try:
        ticker = f"TEST_SP_{uuid.uuid4().hex[:6].upper()}"
        company = CompanyService.create_company(
            db,
            CompanyBase(
                ticker=ticker,
                company_name=f"Test Splitter Company {ticker}",
                exchange="NSE",
                sector="IT",
            ),
        )
        article = {
            "title": "Comprehensive Stock Analysis",
            "article_url": f"https://example.com/news/{uuid.uuid4().hex}",
            "content_hash": uuid.uuid4().hex,
            "summary": "Detailed stock market performance analysis content. " * 50,
            "source": "Economic Times",
        }
        doc, _ = NewsService.ingest(db, company.id, article)

        stored_chunks = ChunkService.chunk_document(db, document=doc)

        assert len(stored_chunks) >= 1
        assert stored_chunks[0].document_id == doc.id
        assert stored_chunks[0].chunk_index == 0
        assert stored_chunks[0].status == "NEW"
    finally:
        db.close()
