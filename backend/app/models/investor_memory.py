import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class InvestorMemory(Base):
    __tablename__ = "investor_memory"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
    )

    risk_profile: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    investment_horizon: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    preferred_sectors: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    avoided_sectors: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    dividend_preference: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship
    user: Mapped["User"] = relationship(
        "User",
        back_populates="investor_memory",
    )
