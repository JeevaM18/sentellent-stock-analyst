import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import uuid
from datetime import datetime, timezone
import pytest  # pyrefly: ignore [missing-import]

from app.db.database import SessionLocal
from app.constants.documents import DOCUMENT_STATUS_NEW
from app.schemas.company import CompanyBase
from app.services.company_service import CompanyService
from app.services.news_service import NewsService


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_company(db):
    ticker = f"TEST_NEWS_{uuid.uuid4().hex[:6].upper()}"
    company = CompanyService.create_company(
        db,
        CompanyBase(
            ticker=ticker,
            company_name=f"Test News Company {ticker}",
            exchange="NSE",
            sector="IT",
        ),
    )
    return company


def test_create_news_article(db, sample_company):
    article = {
        "title": "Reliance Expands Telecom Infrastructure",
        "article_url": f"https://example.com/news/{uuid.uuid4().hex}",
        "content_hash": uuid.uuid4().hex,
        "summary": "Reliance Industries launched new 5G towers today.",
        "published_at": datetime.now(timezone.utc),
        "source": "Economic Times",
    }

    doc, created = NewsService.ingest(db, sample_company.id, article)
    assert created is True
    assert doc.company_id == sample_company.id
    assert doc.title == "Reliance Expands Telecom Infrastructure"
    assert doc.status == DOCUMENT_STATUS_NEW
    assert doc.content_hash == article["content_hash"]
    assert NewsService.needs_embedding(doc) is True


def test_update_duplicate_url(db, sample_company):
    url = f"https://example.com/news/dup_url_{uuid.uuid4().hex}"
    article1 = {
        "title": "Original News Title",
        "article_url": url,
        "content_hash": "hash_1",
        "summary": "Original summary content.",
        "published_at": datetime.now(timezone.utc),
        "source": "Moneycontrol",
    }
    doc1, created1 = NewsService.ingest(db, sample_company.id, article1)
    assert created1 is True

    # Re-ingest with same URL but updated title
    article2 = {
        "title": "Updated News Title",
        "article_url": url,
        "content_hash": "hash_2",
        "summary": "Updated summary content.",
        "published_at": datetime.now(timezone.utc),
        "source": "Moneycontrol",
    }
    doc2, created2 = NewsService.ingest(db, sample_company.id, article2)
    assert created2 is False
    assert doc2.id == doc1.id
    assert doc2.title == "Updated News Title"


def test_update_duplicate_hash(db, sample_company):
    shared_hash = f"hash_shared_{uuid.uuid4().hex}"
    article1 = {
        "title": "Syndicated News Article",
        "article_url": f"https://source1.com/news/{uuid.uuid4().hex}",
        "content_hash": shared_hash,
        "summary": "Syndicated content.",
        "published_at": datetime.now(timezone.utc),
        "source": "Source 1",
    }
    doc1, created1 = NewsService.ingest(db, sample_company.id, article1)
    assert created1 is True

    # Re-ingest with different URL but identical content_hash
    article2 = {
        "title": "Syndicated News Article - Updated",
        "article_url": f"https://source2.com/news/{uuid.uuid4().hex}",
        "content_hash": shared_hash,
        "summary": "Syndicated content updated.",
        "published_at": datetime.now(timezone.utc),
        "source": "Source 2",
    }
    doc2, created2 = NewsService.ingest(db, sample_company.id, article2)
    assert created2 is False
    assert doc2.id == doc1.id


def test_duplicate_title_fallback(db, sample_company):
    pub_date = datetime(2026, 8, 1, 12, 0, 0, tzinfo=timezone.utc)
    title = f"Identical Headline {uuid.uuid4().hex}"

    article1 = {
        "title": title,
        "article_url": f"https://siteA.com/{uuid.uuid4().hex}",
        "content_hash": f"hashA_{uuid.uuid4().hex}",
        "summary": "Headline content site A.",
        "published_at": pub_date,
        "source": "Site A",
    }
    doc1, created1 = NewsService.ingest(db, sample_company.id, article1)
    assert created1 is True

    # Tier 3 fallback check: different URL and different hash, but same title & published_at
    article2 = {
        "title": title,
        "article_url": f"https://siteB.com/{uuid.uuid4().hex}",
        "content_hash": f"hashB_{uuid.uuid4().hex}",
        "summary": "Headline content site B.",
        "published_at": pub_date,
        "source": "Site B",
    }
    doc2, created2 = NewsService.ingest(db, sample_company.id, article2)
    assert created2 is False
    assert doc2.id == doc1.id


def test_bulk_ingest_and_get_needing_embeddings(db, sample_company):
    articles = [
        {
            "title": f"Bulk Article 1 {uuid.uuid4().hex}",
            "article_url": f"https://bulk1.com/{uuid.uuid4().hex}",
            "content_hash": uuid.uuid4().hex,
            "summary": "Bulk 1 summary",
            "published_at": datetime.now(timezone.utc),
            "source": "Source 1",
        },
        {
            "title": f"Bulk Article 2 {uuid.uuid4().hex}",
            "article_url": f"https://bulk2.com/{uuid.uuid4().hex}",
            "content_hash": uuid.uuid4().hex,
            "summary": "Bulk 2 summary",
            "published_at": datetime.now(timezone.utc),
            "source": "Source 2",
        },
    ]

    stats = NewsService.bulk_ingest(db, sample_company.id, articles)
    assert stats["created"] == 2
    assert stats["updated"] == 0
    assert stats["failed"] == 0

    needing = NewsService.get_documents_needing_embeddings(db, limit=100)
    assert len(needing) >= 2


def test_invalid_payload_raises_error(db, sample_company):
    invalid_article = {"invalid_key": "no title or url"}
    with pytest.raises(ValueError, match="Invalid article dictionary payload"):
        NewsService.ingest(db, sample_company.id, invalid_article)
