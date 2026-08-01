from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.embeddings.constants import DEFAULT_EMBEDDING_PROVIDER, EMBEDDING_DIMENSIONS, EMBEDDING_MODEL


def current_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class EmbeddingResult:
    """Dataclass encapsulating generated vector embeddings and metadata."""
    vector: list[float]
    model: str = EMBEDDING_MODEL
    dimensions: int = EMBEDDING_DIMENSIONS
    provider: str = DEFAULT_EMBEDDING_PROVIDER
    text: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=current_utc)


@dataclass(slots=True)
class EmbeddingJob:
    """Dataclass encapsulating a chunk_id and its generated EmbeddingResult for bulk persistence."""
    chunk_id: UUID
    embedding: EmbeddingResult


@dataclass(slots=True)
class EmbeddingPipelineSummary:
    """Dataclass encapsulating embedding batch pipeline execution metrics."""
    processed: int = 0
    created: int = 0
    updated: int = 0
    failed: int = 0
    duration_seconds: float = 0.0
