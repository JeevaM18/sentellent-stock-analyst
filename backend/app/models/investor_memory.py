from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
from sqlalchemy import ForeignKey, String, Text, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import BaseModelMixin

if TYPE_CHECKING:
    from app.models.user import User


class InvestorMemory(BaseModelMixin, Base):
    """
    SQLAlchemy model representing personalized investor memory profile and preferences.
    """

    __tablename__ = "investor_memory"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    risk_profile: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    investment_horizon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    preferred_sectors: Mapped[Optional[list]] = mapped_column(JSONB, default=list, nullable=True)
    avoided_sectors: Mapped[Optional[list]] = mapped_column(JSONB, default=list, nullable=True)
    preferred_market_cap: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    preferred_industries: Mapped[Optional[list]] = mapped_column(JSONB, default=list, nullable=True)
    preferred_assets: Mapped[Optional[list]] = mapped_column(JSONB, default=list, nullable=True)
    investment_style: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dividend_preference: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    esg_preference: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    preferred_hold_period: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    memory_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    memory_facts: Mapped[Optional[list]] = mapped_column(JSONB, default=list, nullable=True)
    memory_source: Mapped[str] = mapped_column(String(50), default="conversation", nullable=False)

    source_message_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    source_conversation_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)

    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    memory_version: Mapped[str] = mapped_column(String(20), default="v1", nullable=False)

    last_confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_updated_from_chat: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[list]] = mapped_column(JSONB, default=list, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="investor_memory")
