from dataclasses import dataclass
from typing import Any

from app.embeddings.constants import DEFAULT_EMBEDDING_PROVIDER, EMBEDDING_DIMENSIONS, EMBEDDING_MODEL


@dataclass(slots=True)
class EmbeddingResult:
    """Dataclass encapsulating generated vector embeddings and metadata."""
    vector: list[float]
    model: str = EMBEDDING_MODEL
    dimensions: int = EMBEDDING_DIMENSIONS
    provider: str = DEFAULT_EMBEDDING_PROVIDER
    text: str | None = None
    metadata: dict[str, Any] | None = None
