import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.dependencies.current_user import get_current_user
from app.investor_memory.builder import MemoryBuilder
from app.investor_memory.schemas import (
    InvestorMemoryRequest,
    InvestorMemoryResponse,
    MemoryContextResponse,
    MemoryStatsResponse,
)
from app.investor_memory.service import InvestorMemoryService
from app.models.user import User

logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("", response_model=InvestorMemoryResponse)
def get_user_memory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch current authenticated user's investor profile memory."""
    memory = InvestorMemoryService.get_or_create_memory(db, current_user.id)
    return memory


@router.put("", response_model=InvestorMemoryResponse)
def update_user_memory(
    payload: InvestorMemoryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually update user's investor profile memory preferences."""
    update_dict = payload.model_dump(exclude_unset=True)
    memory = InvestorMemoryService.update_memory(db, current_user.id, update_dict)
    return memory


@router.delete("")
def delete_user_memory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Clear and delete user's investor profile memory."""
    deleted = InvestorMemoryService.delete_memory(db, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No investor memory profile found to delete.",
        )
    return {"message": "Investor memory profile cleared successfully."}


@router.post("/refresh", response_model=InvestorMemoryResponse)
def refresh_user_memory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rebuild user investor memory profile from full chat conversation history."""
    from app.chat.history import build_chat_history
    from app.services.conversation_service import ConversationService

    conversations = ConversationService.list_conversations(db, current_user.id)
    all_messages = []
    for c in conversations:
        msgs = ConversationService.get_messages(db, c.id)
        all_messages.extend(msgs)

    chat_history = build_chat_history(all_messages)
    memory = InvestorMemoryService.refresh_memory_from_history(db, current_user.id, chat_history)

    if not memory:
        memory = InvestorMemoryService.get_or_create_memory(db, current_user.id)

    return memory


@router.get("/context", response_model=MemoryContextResponse)
def get_memory_context(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Debugging endpoint returning rendered Markdown system prompt context string."""
    memory = InvestorMemoryService.get_memory(db, current_user.id)
    ctx = MemoryBuilder.build(memory)
    return MemoryContextResponse(
        prompt_context=ctx.prompt_context,
        has_profile=ctx.has_profile,
        confidence=ctx.confidence,
        last_updated=ctx.last_updated,
    )


@router.get("/stats", response_model=MemoryStatsResponse)
def get_memory_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return memory statistics for authenticated user profile."""
    summary = InvestorMemoryService.get_summary(db, current_user.id)
    return MemoryStatsResponse(
        user_id=summary.user_id,
        has_profile=summary.has_profile,
        facts_count=summary.facts_count,
        confidence=summary.confidence_score,
        version=summary.memory_version,
        last_updated=summary.last_updated,
    )
