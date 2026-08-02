from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    """Input payload for agentic financial assistant multi-turn conversation."""
    question: str = Field(..., description="User query or financial question")
    conversation_id: UUID | None = Field(default=None, description="Optional conversation UUID for multi-turn history")


class AgentChatResponse(BaseModel):
    """Enriched explainable API response schema."""
    conversation_id: UUID = Field(..., description="Active conversation session UUID")
    answer: str = Field(..., description="Generated grounded response from financial assistant")
    status: str = Field(default="success", description="Status string: 'success' or 'quota_exceeded'")
    retry_after: int | None = Field(default=None, description="Recommended seconds to wait before retrying if rate limited")
    intent: str = Field(default="retrieval", description="Classified query intent or primary tool")
    confidence: float = Field(default=0.85, description="Rule-based confidence score (0.0 to 1.0)")
    reasoning: list[str] = Field(default_factory=list, description="Reasoning trace steps explaining agent execution")
    tools_used: list[str] = Field(default_factory=list, description="List of tools executed by the planner")
    tool_results: dict[str, Any] = Field(default_factory=dict, description="Structured outputs from executed tools")
    citations: list[dict[str, Any]] = Field(default_factory=list, description="Retrieved document citations")
    execution_time_ms: float = Field(default=0.0, description="Total execution latency in milliseconds")
    metadata: dict[str, Any] = Field(default_factory=dict, description="In-memory latency breakdown and observability stats")
