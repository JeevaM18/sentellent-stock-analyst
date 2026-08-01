from uuid import UUID
from pydantic import BaseModel, Field

from app.retrieval.constants import DEFAULT_TOP_K


class Citation(BaseModel):
    """Schema representing a single citation reference for RAG answer grounding."""
    rank: int
    title: str
    source_url: str | None
    ticker: str | None
    similarity: float


class ChatRequest(BaseModel):
    """Request schema for RAG AI chat question answering."""
    query: str = Field(..., description="User question string", min_length=1)
    top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=20, description="Maximum number of context chunks to retrieve")
    company_id: UUID | None = Field(default=None, description="Optional filter by company UUID")
    ticker: str | None = Field(default=None, description="Optional filter by stock ticker (e.g. RELIANCE)")
    conversation_id: UUID | None = Field(default=None, description="Optional conversation UUID for tracking context")
    temperature: float | None = Field(default=None, ge=0.0, le=1.0, description="Optional LLM sampling temperature")
    max_output_tokens: int | None = Field(default=None, ge=64, le=4096, description="Optional max generation tokens")


class ChatResponse(BaseModel):
    """Response schema representing a grounded RAG AI answer with citation metadata and latency breakdown."""
    answer: str
    citations: list[Citation]
    chunks_used: int
    retrieval_time_ms: float
    generation_time_ms: float
    total_time_ms: float
    model: str
    conversation_id: UUID
