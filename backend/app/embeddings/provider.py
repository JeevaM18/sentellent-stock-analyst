from abc import ABC, abstractmethod
from typing import Any

from app.embeddings.types import EmbeddingResult


class BaseEmbeddingProvider(ABC):
    """Abstract base class for vector embedding providers."""

    @abstractmethod
    def embed_text(
        self, *, text: str, metadata: dict[str, Any] | None = None
    ) -> EmbeddingResult:
        """Generate a single vector embedding for the input text."""
        pass

    @abstractmethod
    def embed_batch(
        self, *, texts: list[str], metadatas: list[dict[str, Any]] | None = None
    ) -> list[EmbeddingResult]:
        """Generate vector embeddings for a list of text strings in batch."""
        pass
