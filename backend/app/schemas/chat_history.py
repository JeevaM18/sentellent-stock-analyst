from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """Response schema representing an individual chat message in history."""
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    token_count: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    created_at: datetime


class ConversationResponse(BaseModel):
    """Response schema representing a chat conversation session."""
    id: UUID
    user_id: UUID | None
    title: str
    summary: str | None
    last_message_at: datetime
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ConversationDetailResponse(BaseModel):
    """Response schema representing full conversation detail with messages."""
    conversation: ConversationResponse
    messages: list[MessageResponse]


class ConversationListResponse(BaseModel):
    """Response schema encapsulating paginated conversation list."""
    total: int
    page: int
    limit: int
    conversations: list[ConversationResponse]
