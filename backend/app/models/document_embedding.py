import uuid
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import BaseModelMixin

if TYPE_CHECKING:
    from app.models.knowledge_document import KnowledgeDocument


class DocumentEmbedding(BaseModelMixin, Base):
    __tablename__ = "document_embeddings"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_documents.id"),
        nullable=False,
        index=True,
    )

    embedding = mapped_column(Vector(768))

    embedding_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Relationship
    document: Mapped["KnowledgeDocument"] = relationship(
        "KnowledgeDocument",
        back_populates="embedding",
    )
