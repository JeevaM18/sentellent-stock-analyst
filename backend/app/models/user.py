from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import BaseModelMixin

if TYPE_CHECKING:
    from app.models.user_followed_stock import UserFollowedStock
    from app.models.chat_conversation import ChatConversation
    from app.models.investor_memory import InvestorMemory


class User(BaseModelMixin, Base):
    __tablename__ = "users"

    google_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    profile_picture: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    followed_stocks: Mapped[List["UserFollowedStock"]] = relationship(
        "UserFollowedStock",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    chat_conversations: Mapped[List["ChatConversation"]] = relationship(
        "ChatConversation",
        cascade="all, delete-orphan",
    )

    investor_memory: Mapped[Optional["InvestorMemory"]] = relationship(
        "InvestorMemory",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
