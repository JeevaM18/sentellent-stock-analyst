import logging
from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.chat_conversation import ChatConversation
from app.models.chat_message import ChatMessage

logger = logging.getLogger(__name__)


class ConversationService:
    """Service performing CRUD, security ownership verification, and history management for chat conversations."""

    @staticmethod
    def verify_ownership(conversation: ChatConversation, user_id: UUID | None = None) -> None:
        """Verify user ownership of conversation and enforce 403 Forbidden access security."""
        if conversation.user_id is not None and user_id is not None:
            if conversation.user_id != user_id:
                logger.warning("Unauthorized access attempt: user %s requested conversation %s belonging to %s", user_id, conversation.id, conversation.user_id)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to conversation",
                )

    @staticmethod
    def create_conversation(
        db: Session,
        user_id: UUID | None = None,
        title: str = "New Conversation",
    ) -> ChatConversation:
        """Create a new chat conversation session."""
        now = datetime.now(timezone.utc)
        conversation = ChatConversation(
            user_id=user_id,
            title=title,
            last_message_at=now,
            is_deleted=False,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation(
        db: Session,
        conversation_id: UUID,
        user_id: UUID | None = None,
    ) -> ChatConversation | None:
        """Retrieve conversation by ID enforcing soft delete and ownership verification."""
        conversation = (
            db.query(ChatConversation)
            .filter(
                ChatConversation.id == conversation_id,
                ChatConversation.is_deleted == False,
            )
            .first()
        )
        if conversation:
            ConversationService.verify_ownership(conversation, user_id)
        return conversation

    @staticmethod
    def get_messages(db: Session, conversation_id: UUID) -> list[ChatMessage]:
        """Fetch all chronological messages for a conversation."""
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    @staticmethod
    def append_message(
        db: Session,
        conversation_id: UUID,
        role: str,
        content: str,
        token_count: int | None = None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
    ) -> ChatMessage:
        """Append a user or assistant message to the conversation and update last_message_at timestamp."""
        now = datetime.now(timezone.utc)
        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            created_at=now,
        )
        db.add(message)

        # Update conversation last_message_at timestamp
        conversation = db.query(ChatConversation).filter(ChatConversation.id == conversation_id).first()
        if conversation:
            conversation.last_message_at = now

        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def list_user_conversations(
        db: Session,
        user_id: UUID,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ChatConversation], int]:
        """Fetch paginated conversations belonging to user."""
        q = db.query(ChatConversation).filter(
            ChatConversation.user_id == user_id,
            ChatConversation.is_deleted == False,
        )
        total = q.count()
        offset = (max(1, page) - 1) * limit
        conversations = q.order_by(ChatConversation.last_message_at.desc()).offset(offset).limit(limit).all()
        return conversations, total

    @staticmethod
    def soft_delete_conversation(
        db: Session,
        conversation_id: UUID,
        user_id: UUID | None = None,
    ) -> bool:
        """Soft delete conversation setting is_deleted=True and deleted_at timestamp."""
        conversation = (
            db.query(ChatConversation)
            .filter(
                ChatConversation.id == conversation_id,
                ChatConversation.is_deleted == False,
            )
            .first()
        )
        if not conversation:
            return False

        ConversationService.verify_ownership(conversation, user_id)

        now = datetime.now(timezone.utc)
        conversation.is_deleted = True
        conversation.deleted_at = now
        db.commit()
        return True

    @staticmethod
    def update_conversation_title_if_default(
        db: Session,
        conversation: ChatConversation,
        first_query: str,
    ) -> None:
        """Auto update default 'New Conversation' title based on initial user question."""
        if conversation.title == "New Conversation" and first_query and first_query.strip():
            clean_q = first_query.strip()
            new_title = clean_q[:45] + "..." if len(clean_q) > 45 else clean_q
            conversation.title = new_title
            db.commit()
