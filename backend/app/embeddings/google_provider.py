import os
from typing import Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.embeddings.constants import (
    DEFAULT_EMBEDDING_PROVIDER,
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
)
from app.embeddings.exceptions import EmbeddingProviderError
from app.embeddings.provider import BaseEmbeddingProvider
from app.embeddings.types import EmbeddingResult
from app.embeddings.utils import validate_dimension

load_dotenv()


class GoogleEmbeddingProvider(BaseEmbeddingProvider):
    """
    Google Generative AI vector embedding provider for gemini-embedding-001.
    Lazy-loads SDK client only when embed_text is executed (Zero startup overhead).
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "MOCK_API_KEY"
        self._client = None

    @property
    def client(self) -> genai.Client:
        """Lazy instantiation of genai.Client on first embedding request."""
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def embed_text(
        self, *, text: str, metadata: dict[str, Any] | None = None
    ) -> EmbeddingResult:
        """Generate vector embedding for single text string via gemini-embedding-001."""
        if not text or not text.strip():
            raise ValueError("Text string for embedding cannot be empty")

        try:
            response = self.client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text,
                config=types.EmbedContentConfig(
                    output_dimensionality=EMBEDDING_DIMENSIONS
                ),
            )
        except Exception as exc:
            raise EmbeddingProviderError(f"Google embedding API error: {exc}") from exc

        if not response or not hasattr(response, "embeddings") or not response.embeddings:
            raise EmbeddingProviderError("Empty embedding response returned by Google API")

        vector = response.embeddings[0].values
        validate_dimension(vector)

        return EmbeddingResult(
            vector=vector,
            model=EMBEDDING_MODEL,
            dimensions=EMBEDDING_DIMENSIONS,
            provider=DEFAULT_EMBEDDING_PROVIDER,
            text=text,
            metadata=metadata,
        )

    def embed_batch(
        self, *, texts: list[str], metadatas: list[dict[str, Any]] | None = None
    ) -> list[EmbeddingResult]:
        """Generate vector embeddings for batch of texts preserving input order."""
        results: list[EmbeddingResult] = []
        for index, text in enumerate(texts):
            meta = metadatas[index] if metadatas and index < len(metadatas) else None
            results.append(self.embed_text(text=text, metadata=meta))
        return results
