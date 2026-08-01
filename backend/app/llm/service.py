from app.llm.constants import DEFAULT_MAX_OUTPUT_TOKENS, DEFAULT_TEMPERATURE
from app.llm.google_provider import GoogleLLMProvider
from app.llm.provider import BaseLLMProvider
from app.llm.types import LLMResponse
from app.rag.types import RAGContext


class GenerationService:
    """Service encapsulating LLM generation provider execution for RAG answers."""

    def __init__(self, provider: BaseLLMProvider | None = None):
        self.provider = provider or GoogleLLMProvider()

    def generate(
        self,
        *,
        rag_context: RAGContext,
        temperature: float = DEFAULT_TEMPERATURE,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> LLMResponse:
        """Generate grounded answer using configured LLM provider."""
        return self.provider.generate(
            rag_context=rag_context,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
