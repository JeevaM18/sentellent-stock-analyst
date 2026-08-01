from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def post_chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
):
    """
    End-to-end RAG AI question answering endpoint.
    Performs pgvector search, context assembly, and Gemini LLM answer generation with grounded citations.
    """
    try:
        return ChatService.ask(db=db, request=payload)
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
