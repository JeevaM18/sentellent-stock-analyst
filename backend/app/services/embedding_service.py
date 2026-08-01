from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.constants.chunks import CHUNK_STATUS_EMBEDDED, CHUNK_STATUS_NEW
from app.embeddings.types import EmbeddingJob, EmbeddingResult
from app.embeddings.utils import validate_dimension
from app.models.document_chunk import DocumentChunk
from app.models.document_embedding import DocumentEmbedding


class EmbeddingService:
    """Database service layer for chunk-level vector embeddings in PostgreSQL + pgvector."""

    @staticmethod
    def get_by_chunk(db: Session, chunk_id: UUID) -> DocumentEmbedding | None:
        """Retrieve DocumentEmbedding record for a given chunk_id."""
        return (
            db.query(DocumentEmbedding)
            .filter(DocumentEmbedding.chunk_id == chunk_id)
            .first()
        )

    @staticmethod
    def exists(db: Session, chunk_id: UUID) -> bool:
        """Check if vector embedding exists for a given chunk_id."""
        return (
            db.query(DocumentEmbedding.id)
            .filter(DocumentEmbedding.chunk_id == chunk_id)
            .first()
            is not None
        )

    @staticmethod
    def create(
        db: Session, *, chunk_id: UUID, embedding_result: EmbeddingResult
    ) -> DocumentEmbedding:
        """Create a new DocumentEmbedding record with 768-dimension validation."""
        validate_dimension(embedding_result.vector)

        record = DocumentEmbedding(
            chunk_id=chunk_id,
            embedding=embedding_result.vector,
            provider=embedding_result.provider,
            embedding_model=embedding_result.model,
            dimensions=embedding_result.dimensions,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def update(
        db: Session,
        embedding_record: DocumentEmbedding,
        embedding_result: EmbeddingResult,
    ) -> DocumentEmbedding:
        """Update existing DocumentEmbedding record."""
        validate_dimension(embedding_result.vector)

        embedding_record.embedding = embedding_result.vector
        embedding_record.provider = embedding_result.provider
        embedding_record.embedding_model = embedding_result.model
        embedding_record.dimensions = embedding_result.dimensions

        db.commit()
        db.refresh(embedding_record)
        return embedding_record

    @staticmethod
    def ingest(
        db: Session, *, chunk_id: UUID, embedding_result: EmbeddingResult
    ) -> tuple[DocumentEmbedding, bool]:
        """
        UPSERT vector embedding for a single chunk. Updates DocumentChunk status to 'EMBEDDED'.
        Returns tuple of (DocumentEmbedding, created: bool).
        """
        try:
            record = EmbeddingService.get_by_chunk(db, chunk_id)
            created = False

            if record:
                record = EmbeddingService.update(db, record, embedding_result)
            else:
                record = EmbeddingService.create(db, chunk_id=chunk_id, embedding_result=embedding_result)
                created = True

            # Update parent chunk status and model metadata
            chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
            if chunk:
                chunk.status = CHUNK_STATUS_EMBEDDED
                chunk.embedding_model = embedding_result.model
                db.commit()

            return record, created

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def bulk_ingest(db: Session, jobs: list[EmbeddingJob]) -> dict[str, int]:
        """
        Bulk UPSERT vector embeddings in a single atomic database transaction.
        Returns summary dictionary {"created": c, "updated": u, "failed": f}.
        """
        stats = {"created": 0, "updated": 0, "failed": 0}

        try:
            for job in jobs:
                validate_dimension(job.embedding.vector)

                existing = (
                    db.query(DocumentEmbedding)
                    .filter(DocumentEmbedding.chunk_id == job.chunk_id)
                    .first()
                )

                if existing:
                    existing.embedding = job.embedding.vector
                    existing.provider = job.embedding.provider
                    existing.embedding_model = job.embedding.model
                    existing.dimensions = job.embedding.dimensions
                    stats["updated"] += 1
                else:
                    new_record = DocumentEmbedding(
                        chunk_id=job.chunk_id,
                        embedding=job.embedding.vector,
                        provider=job.embedding.provider,
                        embedding_model=job.embedding.model,
                        dimensions=job.embedding.dimensions,
                    )
                    db.add(new_record)
                    stats["created"] += 1

                # Update DocumentChunk status
                chunk = db.query(DocumentChunk).filter(DocumentChunk.id == job.chunk_id).first()
                if chunk:
                    chunk.status = CHUNK_STATUS_EMBEDDED
                    chunk.embedding_model = job.embedding.model

            db.commit()
            return stats

        except Exception as e:
            db.rollback()
            stats["failed"] = len(jobs)
            raise e

    @staticmethod
    def delete(db: Session, chunk_id: UUID) -> int:
        """Delete vector embedding record for a specific chunk_id."""
        deleted_count = (
            db.query(DocumentEmbedding)
            .filter(DocumentEmbedding.chunk_id == chunk_id)
            .delete()
        )
        db.commit()
        return deleted_count

    @staticmethod
    def get_pending_chunks(
        db: Session, limit: int = 100
    ) -> list[DocumentChunk]:
        """Retrieve DocumentChunks with status 'NEW' ordered by created_at ascending (oldest first)."""
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.status == CHUNK_STATUS_NEW)
            .order_by(DocumentChunk.created_at.asc())
            .limit(limit)
            .all()
        )
