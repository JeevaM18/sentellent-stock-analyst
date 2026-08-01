import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import BaseModelMixin
from app.models.enums import DocumentType

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.document_embedding import DocumentEmbedding
    from app.models.document_chunk import DocumentChunk


class KnowledgeDocument(BaseModelMixin, Base):
    __tablename__ = "knowledge_documents"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
    )

    document_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType, native_enum=False),
        nullable=False,
        index=True,
        default=DocumentType.NEWS,
    )

    title: Mapped[str] = mapped_column(Text, nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    source_url: Mapped[str] = mapped_column(Text, nullable=False, index=True)

    content_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="NEW",
        index=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="documents",
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    embedding: Mapped[Optional["DocumentEmbedding"]] = relationship(
        "DocumentEmbedding",
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def article_url(self) -> str:
        return self.source_url

    @article_url.setter
    def article_url(self, value: str) -> None:
        self.source_url = value
