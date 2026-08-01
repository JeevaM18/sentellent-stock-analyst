from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.dependencies.current_user import get_current_user, get_optional_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.chat_history import (
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationResponse,
    MessageResponse,
)
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/new", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_new_conversation(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Explicitly start a new chat conversation session."""
    user_id = current_user.id if current_user else None
    conv = ConversationService.create_conversation(db, user_id=user_id)
    return ConversationResponse(
        id=conv.id,
        user_id=conv.user_id,
        title=conv.title,
        summary=conv.summary,
        last_message_at=conv.last_message_at,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=0,
    )


@router.post("", response_model=ChatResponse)
def post_chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """
    End-to-end multi-turn RAG AI question answering endpoint.
    Performs memory retention, pgvector search, context assembly, and Gemini LLM answer generation with citations.
    """
    try:
        user_id = current_user.id if current_user else None
        return ChatService.ask(db=db, request=payload, user_id=user_id)
    except HTTPException:
        raise
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        ) from val_err
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG chat question processing failed: {exc}",
        ) from exc


@router.get("/conversations", response_model=ConversationListResponse)
def list_conversations(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch paginated chat conversations belonging to authenticated user."""
    conversations, total = ConversationService.list_user_conversations(
        db,
        user_id=current_user.id,
        page=page,
        limit=limit,
    )

    items = [
        ConversationResponse(
            id=c.id,
            user_id=c.user_id,
            title=c.title,
            summary=c.summary,
            last_message_at=c.last_message_at,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=len(c.messages),
        )
        for c in conversations
    ]

    return ConversationListResponse(
        total=total,
        page=page,
        limit=limit,
        conversations=items,
    )


@router.get("/conversations/{id}", response_model=ConversationDetailResponse)
def get_conversation_detail(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Fetch conversation details and full message history enforcing 403 ownership check."""
    user_id = current_user.id if current_user else None
    conv = ConversationService.get_conversation(db, conversation_id=id, user_id=user_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = ConversationService.get_messages(db, conversation_id=id)

    msg_items = [
        MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            content=m.content,
            token_count=m.token_count,
            prompt_tokens=m.prompt_tokens,
            completion_tokens=m.completion_tokens,
            created_at=m.created_at,
        )
        for m in messages
    ]

    conv_resp = ConversationResponse(
        id=conv.id,
        user_id=conv.user_id,
        title=conv.title,
        summary=conv.summary,
        last_message_at=conv.last_message_at,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=len(messages),
    )

    return ConversationDetailResponse(
        conversation=conv_resp,
        messages=msg_items,
    )


@router.delete("/conversations/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Soft delete conversation enforcing 403 ownership check."""
    user_id = current_user.id if current_user else None
    deleted = ConversationService.soft_delete_conversation(db, conversation_id=id, user_id=user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
