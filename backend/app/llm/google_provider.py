import logging
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.llm.constants import AVAILABLE_MODELS, DEFAULT_MAX_OUTPUT_TOKENS, DEFAULT_MODEL, DEFAULT_PROVIDER, DEFAULT_TEMPERATURE
from app.llm.openrouter_provider import OpenRouterProvider
from app.llm.provider import BaseLLMProvider
from app.llm.types import LLMResponse
from app.rag.types import RAGContext

load_dotenv()
logger = logging.getLogger(__name__)

# Deduplicate environment keys to silence SDK warning
if os.getenv("GOOGLE_API_KEY") and os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY_SECONDARY"] = os.environ.pop("GEMINI_API_KEY")


class QuotaExceededError(Exception):
    """Exception raised when all Gemini & OpenRouter LLM API keys/providers exhaust quota/rate limits."""

    def __init__(self, message: str = "All Gemini & OpenRouter AI model candidates exhausted quota limit.", retry_after: int = 30):
        super().__init__(message)
        self.message = message
        self.retry_after = retry_after


class GoogleLLMProvider(BaseLLMProvider):
    """
    Google Gemini LLM Provider featuring Multi-Key Rotation, Multi-Model Fallback Matrix & OpenRouter Provider Integration:
    1. Collects all configured Gemini API keys (GEMINI_API_KEY, GOOGLE_API_KEY, GEMINI_API_KEY_SECONDARY, etc.)
    2. Iterates across (API_KEY, MODEL) combinations:
       [gemini-3.6-flash -> gemini-3.6-flash-lite -> gemini-2.5-pro -> gemini-2.5-flash -> gemini-1.5-flash]
    3. If Gemini keys/models fail with rate limits (429), fails over to OpenRouterProvider if OPENROUTER_API_KEY is configured.
    """

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        self.model = model
        self.api_keys = []

        if api_key:
            self.api_keys.append(api_key)

        for env_var in ["GOOGLE_API_KEY", "GEMINI_API_KEY", "GEMINI_API_KEY_SECONDARY", "GOOGLE_API_KEY_SECONDARY"]:
            val = os.getenv(env_var)
            if val and val not in self.api_keys and val != "MOCK_API_KEY":
                self.api_keys.append(val)

        if not self.api_keys:
            self.api_keys = ["MOCK_API_KEY"]

    def generate(
        self,
        *,
        rag_context: RAGContext,
        temperature: float = DEFAULT_TEMPERATURE,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> LLMResponse:
        """Generate answer using Multi-Key + Multi-Model Fallback Chain with OpenRouter failover."""
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

        candidate_models = [self.model]
        for m in AVAILABLE_MODELS:
            if m not in candidate_models:
                candidate_models.append(m)

        response = None
        successful_model = None

        # 1. Multi-Key & Multi-Model Rotation Matrix for Gemini
        for key_idx, key in enumerate(self.api_keys, start=1):
            client = genai.Client(api_key=key)
            for target_model in candidate_models:
                try:
                    logger.info("Attempting LLM generation with Key #%d and Model '%s'", key_idx, target_model)
                    response = client.models.generate_content(
                        model=target_model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=temperature,
                            max_output_tokens=max_output_tokens,
                        ),
                    )
                    successful_model = target_model
                    break  # Success!
                except Exception as exc:
                    exc_str = str(exc)
                    if "429" in exc_str or "RESOURCE_EXHAUSTED" in exc_str or "Quota exceeded" in exc_str:
                        logger.warning("Key #%d with Model '%s' rate limited (429). Trying next key/model...", key_idx, target_model)
                        continue
                    elif "404" in exc_str or "NOT_FOUND" in exc_str or "not found" in exc_str.lower():
                        logger.warning("Key #%d with Model '%s' not found (404). Trying next model...", key_idx, target_model)
                        continue
                    else:
                        logger.warning("Key #%d with Model '%s' error: %s. Trying next candidate...", key_idx, target_model, exc)
                        continue
            if response and successful_model:
                break  # Outer key loop exit on success

        if response and successful_model:
            answer_text = response.text if response and hasattr(response, "text") and response.text else "I couldn't find enough evidence in the retrieved documents to answer your question."
            input_tokens = getattr(response.usage_metadata, "prompt_token_count", None) if hasattr(response, "usage_metadata") else None
            output_tokens = getattr(response.usage_metadata, "candidates_token_count", None) if hasattr(response, "usage_metadata") else None
            finish_reason = None
            if hasattr(response, "candidates") and response.candidates and hasattr(response.candidates[0], "finish_reason"):
                finish_reason = str(response.candidates[0].finish_reason)

            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return LLMResponse(
                answer=answer_text,
                model=successful_model,
                provider=DEFAULT_PROVIDER,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                finish_reason=finish_reason,
                latency_ms=latency_ms,
            )

        # 2. OpenRouter Provider Failover Integration
        if os.getenv("OPENROUTER_API_KEY"):
            logger.info("Gemini candidates exhausted rate limits. Trying OpenRouter...")
            try:
                openrouter_provider = OpenRouterProvider()
                return openrouter_provider.generate(
                    rag_context=rag_context,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                )
            except Exception as or_exc:
                logger.warning("OpenRouter failed: %s", or_exc)

        logger.error("All Gemini API keys & OpenRouter provider candidates exhausted or failed.")
        raise QuotaExceededError(
            message="All configured Gemini API keys and OpenRouter fallback candidates reached rate limits.",
            retry_after=30,
        )
