from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.constants.documents import DOCUMENT_STATUS_NEW, DOCUMENT_TYPE_NEWS
from app.models.enums import DocumentType
from app.models.knowledge_document import KnowledgeDocument
from app.ingestion.news.utils import normalize_url


class BaseNewsIngestionService(ABC):
    """Abstract base class for news ingestion services."""

    @abstractmethod
    def ingest(self, db: Session, *args: Any, **kwargs: Any) -> Any:
        pass


class NewsService(BaseNewsIngestionService):

    @staticmethod
    def get_by_url(db: Session, article_url: str) -> KnowledgeDocument | None:
        """Find existing KnowledgeDocument by normalized source URL."""
        if not article_url:
            return None
        clean_url = normalize_url(article_url)
        return (
            db.query(KnowledgeDocument)
            .filter(KnowledgeDocument.source_url == clean_url)
            .first()
        )

    @staticmethod
    def get_by_hash(db: Session, content_hash: str) -> KnowledgeDocument | None:
        """Find existing KnowledgeDocument by SHA256 content hash."""
        if not content_hash:
            return None
        return (
            db.query(KnowledgeDocument)
            .filter(KnowledgeDocument.content_hash == content_hash)
            .first()
        )

    @staticmethod
    def get_by_title_and_date(
        db: Session, company_id: UUID, title: str, published_at: datetime | None
    ) -> KnowledgeDocument | None:
        """Fallback 3rd-tier deduplication by company, title, and published timestamp."""
        if not title or not company_id:
            return None
        query = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.company_id == company_id,
            KnowledgeDocument.title == title.strip(),
        )
        if published_at:
            query = query.filter(KnowledgeDocument.published_at == published_at)
        return query.first()

    @staticmethod
    def get_documents_needing_embeddings(
        db: Session, limit: int = 100
    ) -> list[KnowledgeDocument]:
        """Retrieve KnowledgeDocuments with status 'NEW' awaiting chunking and vector embedding."""
        return (
            db.query(KnowledgeDocument)
            .filter(KnowledgeDocument.status == DOCUMENT_STATUS_NEW)
            .order_by(KnowledgeDocument.created_at.asc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def needs_embedding(document: KnowledgeDocument) -> bool:
        """Helper checking if a document status is 'NEW' awaiting vector embeddings."""
        return document.status == DOCUMENT_STATUS_NEW

    @staticmethod
    def create(
        db: Session, company_id: UUID, article: dict[str, Any]
    ) -> KnowledgeDocument:
        """Create a new KnowledgeDocument with NEW status."""
        doc = KnowledgeDocument(
            company_id=company_id,
            document_type=DocumentType.NEWS,
            title=article.get("title", "Untitled News").strip(),
            content=article.get("summary", article.get("title", "")).strip(),
            summary=article.get("summary"),
            source=article.get("source", "Google News"),
            source_url=normalize_url(article.get("article_url", "")),
            content_hash=article.get("content_hash"),
            published_at=article.get("published_at"),
            status=DOCUMENT_STATUS_NEW,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def update(
        db: Session, document: KnowledgeDocument, article: dict[str, Any]
    ) -> KnowledgeDocument:
        """Update existing KnowledgeDocument without altering created_at or status."""
        document.title = article.get("title", document.title).strip()
        document.content = article.get("summary", document.content).strip()
        document.summary = article.get("summary", document.summary)
        document.source = article.get("source", document.source)
        if article.get("article_url"):
            document.source_url = normalize_url(article["article_url"])
        if article.get("content_hash"):
            document.content_hash = article["content_hash"]
        if article.get("published_at"):
            document.published_at = article["published_at"]

        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def ingest(
        db: Session, company_id: UUID, article: dict[str, Any]
    ) -> tuple[KnowledgeDocument, bool]:
        """
        Ingest single article with 3-tier fallback deduplication (URL -> Hash -> Title+Date).
        Returns tuple of (KnowledgeDocument, created: bool).
        """
        if not isinstance(article, dict) or not article.get("title"):
            raise ValueError("Invalid article dictionary payload")

        try:
            # Tier 1: Search by normalized article URL
            doc = NewsService.get_by_url(db, article.get("article_url", ""))

            # Tier 2: Search by SHA256 content hash
            if not doc and article.get("content_hash"):
                doc = NewsService.get_by_hash(db, article["content_hash"])

            # Tier 3: Fallback search by company + title + published_at
            if not doc:
                doc = NewsService.get_by_title_and_date(
                    db, company_id, article.get("title", ""), article.get("published_at")
                )

            if doc:
                updated_doc = NewsService.update(db, doc, article)
                return updated_doc, False
            else:
                new_doc = NewsService.create(db, company_id, article)
                return new_doc, True

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def bulk_ingest(
        db: Session, company_id: UUID, articles: list[dict[str, Any]]
    ) -> dict[str, int]:
        """
        Bulk ingest list of news articles for a company.
        Returns summary breakdown dict: {"created": c, "updated": u, "failed": f, "duplicates": d}.
        """
        stats = {"created": 0, "updated": 0, "failed": 0, "duplicates": 0}

        for article in articles:
            try:
                _, created = NewsService.ingest(db, company_id, article)
                if created:
                    stats["created"] += 1
                else:
                    stats["updated"] += 1
                    stats["duplicates"] += 1
            except Exception:
                stats["failed"] += 1

        return stats
