from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import BaseModelMixin

if TYPE_CHECKING:
    from app.models.company_fundamentals import CompanyFundamentals
    from app.models.knowledge_document import KnowledgeDocument
    from app.models.user_followed_stock import UserFollowedStock


class Company(BaseModelMixin, Base):
    __tablename__ = "companies"

    ticker: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    exchange: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    sector: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    industry: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Relationships
    fundamentals: Mapped[Optional["CompanyFundamentals"]] = relationship(
        "CompanyFundamentals",
        back_populates="company",
        uselist=False,
        cascade="all, delete-orphan",
    )

    documents: Mapped[List["KnowledgeDocument"]] = relationship(
        "KnowledgeDocument",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    followers: Mapped[List["UserFollowedStock"]] = relationship(
        "UserFollowedStock",
        back_populates="company",
        cascade="all, delete-orphan",
    )
