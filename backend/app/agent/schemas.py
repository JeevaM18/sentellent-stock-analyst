from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    """Payload schema for Agentic AI chat requests."""
    question: str = Field(..., min_length=1, description="Financial inquiry or market question.")
    conversation_id: UUID | None = Field(default=None, description="Optional existing conversation session ID.")


class AgentChatResponse(BaseModel):
    """Response schema returned by the Agent API endpoint."""
    answer: str
    conversation_id: UUID
    intent: str = Field(default="retrieval", description="Classified query intent category.")
    execution_time_ms: float
    agent_version: str
    tools_used: list[str] = Field(default_factory=list)
    tool_results: dict[str, Any] = Field(default_factory=dict)
    citations: list[dict[str, Any]] = Field(default_factory=list)
