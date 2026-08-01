import logging
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.llm.constants import DEFAULT_MAX_OUTPUT_TOKENS, DEFAULT_MODEL, DEFAULT_PROVIDER, DEFAULT_TEMPERATURE
from app.llm.provider import BaseLLMProvider
from app.llm.types import LLMResponse
from app.rag.types import RAGContext

load_dotenv()
logger = logging.getLogger(__name__)


class GoogleLLMProvider(BaseLLMProvider):
    """Google Gemini LLM provider for RAG answer generation using gemini-flash-latest."""

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not key:
            key = "MOCK_API_KEY"
        self.client = genai.Client(api_key=key)
        self.model = model

    def generate(
        self,
        *,
        rag_context: RAGContext,
        temperature: float = DEFAULT_TEMPERATURE,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> LLMResponse:
        """Generate answer using Google Gemini models.generate_content()."""
        start_time = time.perf_counter()

        context_body = rag_context.context.strip() if rag_context.context and rag_context.context.strip() else "No context available."
        history_body = rag_context.chat_history.strip() if rag_context.chat_history and rag_context.chat_history.strip() else "No prior conversation history."

        prompt = (
            "=========================\n"
            "SYSTEM\n"
            "=========================\n"
            f"{rag_context.system_prompt}\n\n"
            "=========================\n"
            "CHAT HISTORY\n"
            "=========================\n"
            f"{history_body}\n\n"
            "=========================\n"
            "RETRIEVED CONTEXT\n"
            "=========================\n"
            f"{context_body}\n\n"
            "=========================\n"
            "CURRENT QUESTION\n"
            "=========================\n"
            f"{rag_context.question}"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                ),
            )
        except Exception as exc:
            logger.error("Gemini LLM generate_content error: %s", exc)
            raise RuntimeError(f"Google Gemini generation error: {exc}") from exc

        answer_text = response.text if response and hasattr(response, "text") and response.text else "I couldn't find enough evidence in the retrieved documents to answer your question."

        input_tokens = None
        output_tokens = None
        finish_reason = None

        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = response.usage_metadata
            input_tokens = getattr(usage, "prompt_token_count", None)
            output_tokens = getattr(usage, "candidates_token_count", None)

        if hasattr(response, "candidates") and response.candidates:
            cand = response.candidates[0]
            if hasattr(cand, "finish_reason"):
                finish_reason = str(cand.finish_reason)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return LLMResponse(
            answer=answer_text,
            model=self.model,
            provider=DEFAULT_PROVIDER,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            finish_reason=finish_reason,
            latency_ms=latency_ms,
        )
