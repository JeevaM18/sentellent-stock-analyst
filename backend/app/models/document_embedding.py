import uuid
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import BaseModelMixin

if TYPE_CHECKING:
    from app.models.document_chunk import DocumentChunk


class DocumentEmbedding(BaseModelMixin, Base):
    __tablename__ = "document_embeddings"
    __table_args__ = (
        UniqueConstraint("chunk_id", name="uq_document_embeddings_chunk_id"),
    )

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    embedding = mapped_column(Vector(768), nullable=False)

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="google",
    )

    embedding_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="text-embedding-004",
    )

    dimensions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=768,
    )

    # Relationship
    chunk: Mapped["DocumentChunk"] = relationship(
        "DocumentChunk",
        back_populates="embedding",
    )
