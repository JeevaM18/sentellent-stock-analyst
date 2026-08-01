from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agent.schemas import AgentChatRequest, AgentChatResponse
from app.agent.service import AgentService
from app.db.database import SessionLocal
from app.dependencies.current_user import get_optional_current_user
from app.models.user import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=AgentChatResponse)
def post_agent_chat(
    payload: AgentChatRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """
    Agentic AI chat endpoint executing LangGraph StateGraph workflow with multi-tool planner & memory.
    """
    try:
        user_id = current_user.id if current_user else None
        result_state = AgentService.run(
            db=db,
            question=payload.question,
            user_id=user_id,
            conversation_id=payload.conversation_id,
        )

        metadata = result_state.get("metadata", {})
        return AgentChatResponse(
            answer=result_state.get("final_answer", ""),
            conversation_id=result_state["conversation_id"],
            intent=metadata.get("intent", "retrieval"),
            confidence=metadata.get("confidence", 0.85),
            reasoning=metadata.get("reasoning", []),
            tools_used=metadata.get("tools_used", []),
            tool_results=result_state.get("tool_results", {}),
            citations=result_state.get("citations", []),
            execution_time_ms=metadata.get("execution_time_ms", 0.0),
            metadata=metadata,
        )
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
            detail=f"Agent workflow execution failed: {exc}",
        ) from exc
