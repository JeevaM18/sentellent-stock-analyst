import logging
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

from app.llm.constants import DEFAULT_MAX_OUTPUT_TOKENS, DEFAULT_TEMPERATURE
from app.llm.provider import BaseLLMProvider
from app.llm.types import LLMResponse
from app.rag.types import RAGContext

load_dotenv()
logger = logging.getLogger(__name__)


class OpenRouterProvider(BaseLLMProvider):
    """
    OpenRouter LLM provider using OpenAI Python SDK configured for OpenRouter.
    Base URL: https://openrouter.ai/api/v1
    Supports multi-model failover via OPENROUTER_MODELS (e.g. qwen/qwen3.5-flash-02-23,qwen/qwen3.6-flash,deepseek/deepseek-chat)
    """

    def __init__(self, api_key: str | None = None, models: list[str] | str | None = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")

        raw_models = []
        if models:
            if isinstance(models, list):
                raw_models = models
            else:
                raw_models = [m.strip() for m in models.split(",") if m.strip()]
        else:
            env_models_str = os.getenv("OPENROUTER_MODELS")
            if env_models_str:
                raw_models = [m.strip() for m in env_models_str.split(",") if m.strip()]
            elif os.getenv("OPENROUTER_MODEL"):
                raw_models = [os.getenv("OPENROUTER_MODEL").strip()]
            else:
                raw_models = ["qwen/qwen3.5-flash-02-23", "qwen/qwen3.6-flash", "deepseek/deepseek-chat"]

        # Filter out outdated placeholder model IDs like 'qwen/qwen3' if present
        self.models = [m for m in raw_models if m != "qwen/qwen3"]
        if not self.models:
            self.models = ["qwen/qwen3.5-flash-02-23", "qwen/qwen3.6-flash", "deepseek/deepseek-chat"]

        if self.api_key:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                default_headers={
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Sentellent AI",
                },
            )
        else:
            self.client = None

    def generate(
        self,
        *,
        rag_context: RAGContext,
        temperature: float = DEFAULT_TEMPERATURE,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> LLMResponse:
        """Generate LLM answer iterating through configured OpenRouter candidate models."""
        start_time = time.perf_counter()

        if not self.api_key or not self.client:
            logger.warning("OpenRouter failed: OPENROUTER_API_KEY is not set.")
            raise RuntimeError("OPENROUTER_API_KEY is not set.")

        context_body = rag_context.context.strip() if rag_context.context and rag_context.context.strip() else "No context available."
        history_body = rag_context.chat_history.strip() if rag_context.chat_history and rag_context.chat_history.strip() else "No prior conversation history."

        system_prompt_combined = (
            f"{rag_context.system_prompt}\n\n"
            f"=========================\n"
            f"RETRIEVED CONTEXT\n"
            f"=========================\n"
            f"{context_body}"
        )

        user_prompt_combined = (
            f"=========================\n"
            f"CHAT HISTORY\n"
            f"=========================\n"
            f"{history_body}\n\n"
            f"=========================\n"
            f"CURRENT QUESTION\n"
            f"=========================\n"
            f"{rag_context.question}"
        )

        for target_model in self.models:
            logger.info("Trying OpenRouter model: %s", target_model)
            try:
                completion = self.client.chat.completions.create(
                    model=target_model,
                    messages=[
                        {"role": "system", "content": system_prompt_combined},
                        {"role": "user", "content": user_prompt_combined},
                    ],
                    temperature=temperature,
                    max_tokens=max_output_tokens,
                )

                answer_text = (
                    completion.choices[0].message.content
                    if completion and completion.choices and completion.choices[0].message
                    else "I couldn't find enough evidence in the retrieved documents to answer your question."
                )

                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                logger.info("OpenRouter model %s succeeded.", target_model)

                input_tokens = getattr(completion.usage, "prompt_tokens", None) if hasattr(completion, "usage") else None
                output_tokens = getattr(completion.usage, "completion_tokens", None) if hasattr(completion, "usage") else None

                return LLMResponse(
                    answer=answer_text,
                    model=target_model,
                    provider="openrouter",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    finish_reason="stop",
                    latency_ms=latency_ms,
                )
            except Exception as exc:
                logger.warning("OpenRouter model %s failed: %s", target_model, exc)
                continue

        logger.warning("OpenRouter failed: all models (%s) failed.", self.models)
        raise RuntimeError(f"All OpenRouter models ({', '.join(self.models)}) failed.")
