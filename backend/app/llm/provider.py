from abc import ABC, abstractmethod

from app.llm.constants import DEFAULT_MAX_OUTPUT_TOKENS, DEFAULT_TEMPERATURE
from app.llm.types import LLMResponse
from app.rag.types import RAGContext


class BaseLLMProvider(ABC):
    """Abstract interface for LLM text generation providers."""

    @abstractmethod
    def generate(
        self,
        *,
        rag_context: RAGContext,
        temperature: float = DEFAULT_TEMPERATURE,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> LLMResponse:
        """Generate LLM answer text grounded in RAGContext."""
        pass
