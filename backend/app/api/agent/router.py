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
    Handles quota limits (429) gracefully returning RAG fallback evidence and retry seconds.
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
        status_str = metadata.get("status", "success")
        retry_after = metadata.get("retry_after")

        return AgentChatResponse(
            answer=result_state.get("final_answer", ""),
            conversation_id=result_state["conversation_id"],
            status=status_str,
            retry_after=retry_after,
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
        exc_str = str(exc)
        if "429" in exc_str or "RESOURCE_EXHAUSTED" in exc_str or "Quota exceeded" in exc_str:
            return AgentChatResponse(
                answer="The Gemini AI model is currently rate limited (5 req/min). Showing retrieved evidence and company fundamental data below.",
                conversation_id=payload.conversation_id or "00000000-0000-0000-0000-000000000000",
                status="quota_exceeded",
                retry_after=30,
                intent="retrieval",
                confidence=0.80,
                reasoning=["Gemini 429 Rate Limit Detected", "Switched to RAG retrieval fallback mode"],
                tools_used=["retrieval"],
                tool_results={},
                citations=[],
                execution_time_ms=100.0,
                metadata={"quota_exceeded": True, "retry_after": 30},
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent workflow execution failed: {exc}",
        ) from exc
