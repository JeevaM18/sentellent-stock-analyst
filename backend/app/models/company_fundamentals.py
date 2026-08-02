import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import BaseModelMixin

if TYPE_CHECKING:
    from app.models.company import Company


class CompanyFundamentals(BaseModelMixin, Base):
    __tablename__ = "company_fundamentals"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        unique=True,
        nullable=False,
        index=True,
    )

    current_price: Mapped[float | None] = mapped_column(
        DECIMAL(12, 4),
        nullable=True,
    )

    market_cap: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    shares_outstanding: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    pe_ratio: Mapped[float | None] = mapped_column(
        DECIMAL(12, 4),
        nullable=True,
    )

    eps: Mapped[float | None] = mapped_column(
        DECIMAL(12, 4),
        nullable=True,
    )

    roe: Mapped[float | None] = mapped_column(
        DECIMAL(12, 4),
        nullable=True,
    )

    debt_to_equity: Mapped[float | None] = mapped_column(
        DECIMAL(12, 4),
        nullable=True,
    )

    dividend_yield: Mapped[float | None] = mapped_column(
        DECIMAL(12, 4),
        nullable=True,
    )

    book_value: Mapped[float | None] = mapped_column(
        DECIMAL(12, 4),
        nullable=True,
    )

    price_to_book: Mapped[float | None] = mapped_column(
        DECIMAL(12, 4),
        nullable=True,
    )

    beta: Mapped[float | None] = mapped_column(
        DECIMAL(12, 4),
        nullable=True,
    )

    fifty_two_week_high: Mapped[float | None] = mapped_column(
        DECIMAL(12, 4),
        nullable=True,
    )

    fifty_two_week_low: Mapped[float | None] = mapped_column(
        DECIMAL(12, 4),
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="INR",
    )

    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="fundamentals",
    )
