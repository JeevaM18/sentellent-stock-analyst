from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.retrieval.constants import DEFAULT_MIN_SIMILARITY, DEFAULT_TOP_K


class RetrievalSearchRequest(BaseModel):
    """Request schema for semantic vector retrieval search."""
    query: str = Field(..., description="User search query string", min_length=1)
    top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=20, description="Maximum number of chunks to return")
    min_similarity: float = Field(default=DEFAULT_MIN_SIMILARITY, ge=0.0, le=1.0, description="Minimum cosine similarity threshold")
    company_id: UUID | None = Field(default=None, description="Optional filter by company UUID")
    ticker: str | None = Field(default=None, description="Optional filter by stock ticker (e.g. RELIANCE)")
    published_after: datetime | None = Field(default=None, description="Optional filter for documents published after timestamp")


class RetrievalChunkResponse(BaseModel):
    """Response schema representing a single retrieved document chunk."""
    chunk_id: UUID
    document_id: UUID
    company_id: UUID | None
    ticker: str | None
    company_name: str | None
    distance: float
    similarity: float
    content: str
    chunk_index: int
    source_title: str
    source_url: str
    published_at: datetime | None


class RetrievalResponse(BaseModel):
    """Response schema encapsulating semantic retrieval search results."""
    query: str
    total: int
    duration_ms: float
    chunks: list[RetrievalChunkResponse]
