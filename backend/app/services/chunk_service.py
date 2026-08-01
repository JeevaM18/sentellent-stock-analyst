from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.constants.chunks import CHUNK_STATUS_NEW
from app.models.document_chunk import DocumentChunk


class ChunkService:

    @staticmethod
    def create_chunk(
        db: Session,
        *,
        document_id: UUID,
        chunk_index: int,
        content: str,
        chunk_hash: str,
        token_count: int,
        character_count: int,
        start_char: int | None = None,
        end_char: int | None = None,
        status: str = CHUNK_STATUS_NEW,
        embedding_model: str | None = None,
    ) -> DocumentChunk:
        """Create a single DocumentChunk record."""
        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            chunk_hash=chunk_hash,
            token_count=token_count,
            character_count=character_count,
            start_char=start_char,
            end_char=end_char,
            status=status,
            embedding_model=embedding_model,
        )
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        return chunk

    @staticmethod
    def get_chunks(db: Session, document_id: UUID) -> list[DocumentChunk]:
        """Retrieve all DocumentChunks for a document ordered by chunk_index ascending."""
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .all()
        )

    @staticmethod
    def delete_chunks(db: Session, document_id: UUID) -> int:
        """Delete all DocumentChunks associated with a document."""
        deleted_count = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .delete()
        )
        db.commit()
        return deleted_count

    @staticmethod
    def replace_chunks(
        db: Session, document_id: UUID, chunks_data: list[dict[str, Any]]
    ) -> list[DocumentChunk]:
        """
        Atomically delete existing DocumentChunks for a document and insert new chunks.
        Prevents duplicate index conflicts during re-chunking.
        """
        try:
            db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()

            new_chunks = []
            for item in chunks_data:
                chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=item["chunk_index"],
                    content=item["content"],
                    chunk_hash=item["chunk_hash"],
                    token_count=item["token_count"],
                    character_count=item.get("character_count", len(item["content"])),
                    start_char=item.get("start_char"),
                    end_char=item.get("end_char"),
                    status=item.get("status", CHUNK_STATUS_NEW),
                    embedding_model=item.get("embedding_model"),
                )
                db.add(chunk)
                new_chunks.append(chunk)

            db.commit()
            for chunk in new_chunks:
                db.refresh(chunk)

            new_chunks.sort(key=lambda c: c.chunk_index)
            return new_chunks

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def get_chunks_needing_embeddings(
        db: Session, limit: int = 100
    ) -> list[DocumentChunk]:
        """Fetch DocumentChunks with status 'NEW' awaiting vector embeddings."""
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.status == CHUNK_STATUS_NEW)
            .order_by(DocumentChunk.created_at.asc())
            .limit(limit)
            .all()
        )
