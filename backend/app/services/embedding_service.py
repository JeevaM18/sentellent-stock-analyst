from uuid import UUID
from sqlalchemy.orm import Session

from app.constants.chunks import CHUNK_STATUS_NEW
from app.models.document_chunk import DocumentChunk
from app.models.document_embedding import DocumentEmbedding


class EmbeddingService:
    """Database service layer operating at the chunk level for document vector embeddings."""

    @staticmethod
    def get_embedding(db: Session, chunk_id: UUID) -> DocumentEmbedding | None:
        """Retrieve DocumentEmbedding record for a specific chunk_id."""
        return (
            db.query(DocumentEmbedding)
            .filter(DocumentEmbedding.chunk_id == chunk_id)
            .first()
        )

    @staticmethod
    def exists(db: Session, chunk_id: UUID) -> bool:
        """Check if vector embedding already exists for a given chunk_id."""
        return (
            db.query(DocumentEmbedding.id)
            .filter(DocumentEmbedding.chunk_id == chunk_id)
            .first()
            is not None
        )

    @staticmethod
    def delete_embedding(db: Session, chunk_id: UUID) -> int:
        """Delete vector embedding associated with a given chunk_id."""
        deleted_count = (
            db.query(DocumentEmbedding)
            .filter(DocumentEmbedding.chunk_id == chunk_id)
            .delete()
        )
        db.commit()
        return deleted_count

    @staticmethod
    def get_chunks_needing_embeddings(
        db: Session, limit: int = 100
    ) -> list[DocumentChunk]:
        """Retrieve DocumentChunks with status 'NEW' awaiting vector embeddings."""
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.status == CHUNK_STATUS_NEW)
            .order_by(DocumentChunk.created_at.asc())
            .limit(limit)
            .all()
        )
