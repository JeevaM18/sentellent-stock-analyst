import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import BaseModelMixin
from app.models.enums import ChatRole

if TYPE_CHECKING:
    from app.models.chat_session import ChatSession


class ChatMessage(BaseModelMixin, Base):
    __tablename__ = "chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id"),
        nullable=False,
        index=True,
    )

    role: Mapped[ChatRole] = mapped_column(
        SQLEnum(ChatRole, native_enum=False),
        nullable=False,
        default=ChatRole.USER,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Relationship
    session: Mapped["ChatSession"] = relationship(
        "ChatSession",
        back_populates="messages",
    )
