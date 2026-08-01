from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class RetrievalResult:
    """Dataclass representing a single retrieved document chunk with semantic scores and metadata."""
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
    published_at: datetime | None = None


@dataclass(slots=True)
class RetrievalSummary:
    """Dataclass encapsulating complete search query retrieval results and performance metrics."""
    query: str
    total: int = 0
    duration_seconds: float = 0.0
    results: list[RetrievalResult] = field(default_factory=list)
