from typing import Any, TypedDict
from uuid import UUID


class AgentState(TypedDict):
    """
    TypedDict representing the full execution state passed across LangGraph nodes.
    """
    user_id: UUID | None
    conversation_id: UUID | None
    question: str
    chat_history: str
    context: str
    retrieved_context: str
    tool_results: dict[str, Any]
    final_answer: str
    citations: list[dict[str, Any]]
    metadata: dict[str, Any]
    iteration: int
    services: dict[str, Any]
