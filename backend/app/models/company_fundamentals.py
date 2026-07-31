import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, ForeignKey, BigInteger
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
        nullable=False,
        index=True,
    )

    market_cap: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    pe_ratio: Mapped[float | None] = mapped_column(
        DECIMAL(10, 2),
        nullable=True,
    )

    eps: Mapped[float | None] = mapped_column(
        DECIMAL(10, 2),
        nullable=True,
    )

    roe: Mapped[float | None] = mapped_column(
        DECIMAL(10, 2),
        nullable=True,
    )

    debt_to_equity: Mapped[float | None] = mapped_column(
        DECIMAL(10, 2),
        nullable=True,
    )

    dividend_yield: Mapped[float | None] = mapped_column(
        DECIMAL(10, 2),
        nullable=True,
    )

    book_value: Mapped[float | None] = mapped_column(
        DECIMAL(10, 2),
        nullable=True,
    )

    # Relationship
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="fundamentals",
    )
