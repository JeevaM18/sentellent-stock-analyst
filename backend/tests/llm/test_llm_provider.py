import sys
import os
from unittest.mock import patch, MagicMock
import pytest

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.llm.google_provider import GoogleLLMProvider, QuotaExceededError
from app.llm.openrouter_provider import OpenRouterProvider
from app.llm.types import LLMResponse
from app.rag.types import RAGContext


@patch("app.llm.google_provider.genai.Client")
def test_generate_success(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.text = "Reliance Industries reported Q1 growth due to strong energy and retail demand."
    mock_response.usage_metadata = MagicMock(prompt_token_count=150, candidates_token_count=45)
    mock_response.candidates = [MagicMock(finish_reason="STOP")]
    mock_client.models.generate_content.return_value = mock_response

    provider = GoogleLLMProvider(api_key="test-key")
    ctx = RAGContext(
        question="Why did Reliance grow?",
        system_prompt="Answer strictly from context.",
        context="[Chunk 1] Reliance Q1 revenue grew in energy.",
        chunks=[],
    )

    res = provider.generate(rag_context=ctx)

    assert isinstance(res, LLMResponse)
    assert "Reliance Industries reported Q1 growth" in res.answer
    assert res.provider == "google"
    assert res.input_tokens == 150
    assert res.output_tokens == 45
    assert res.finish_reason == "STOP"
    assert res.latency_ms >= 0.0


@patch("app.llm.google_provider.genai.Client")
def test_empty_context(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.text = "I couldn't find enough evidence in the retrieved documents to answer your question."
    mock_client.models.generate_content.return_value = mock_response

    provider = GoogleLLMProvider(api_key="test-key")
    ctx = RAGContext(
        question="Unknown stock question?",
        system_prompt="Answer strictly from context.",
        context="",
        chunks=[],
    )

    res = provider.generate(rag_context=ctx)
    assert "I couldn't find enough evidence" in res.answer


@patch("app.llm.google_provider.OpenRouterProvider")
@patch("app.llm.google_provider.genai.Client")
def test_provider_failure(mock_client_cls, mock_openrouter_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.models.generate_content.side_effect = Exception("API Connection Timeout")

    mock_or_instance = MagicMock()
    mock_or_instance.generate.side_effect = Exception("OpenRouter Timeout")
    mock_openrouter_cls.return_value = mock_or_instance

    provider = GoogleLLMProvider(api_key="test-key")
    ctx = RAGContext(question="Fail test", system_prompt="Sys", context="Ctx", chunks=[])

    with pytest.raises(QuotaExceededError):
        provider.generate(rag_context=ctx)


@patch("openai.resources.chat.completions.Completions.create")
def test_openrouter_provider_success(mock_create):
    mock_choice = MagicMock()
    mock_choice.message.content = "OpenRouter response for TCS stock analysis."
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    mock_completion.usage = MagicMock(prompt_tokens=100, completion_tokens=30)
    mock_create.return_value = mock_completion

    provider = OpenRouterProvider(api_key="test-openrouter-key")
    ctx = RAGContext(
        question="Analyze TCS stock",
        system_prompt="Answer from context.",
        context="[Chunk 1] TCS revenue increased.",
        chunks=[],
    )

    res = provider.generate(rag_context=ctx)
    assert isinstance(res, LLMResponse)
    assert res.provider == "openrouter"
    assert "OpenRouter response" in res.answer
    assert res.input_tokens == 100
    assert res.output_tokens == 30


@patch("openai.resources.chat.completions.Completions.create")
def test_openrouter_provider_multi_model_fallback(mock_create):
    mock_choice = MagicMock()
    mock_choice.message.content = "DeepSeek secondary fallback answer."
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    mock_completion.usage = MagicMock(prompt_tokens=80, completion_tokens=25)

    mock_create.side_effect = [
        Exception("429 Rate limit reached for qwen/qwen3.5-flash-02-23"),
        mock_completion,
    ]

    provider = OpenRouterProvider(api_key="test-openrouter-key", models=["qwen/qwen3.5-flash-02-23", "deepseek/deepseek-chat"])
    ctx = RAGContext(
        question="Fallback query",
        system_prompt="System",
        context="Context",
        chunks=[],
    )

    res = provider.generate(rag_context=ctx)
    assert isinstance(res, LLMResponse)
    assert res.provider == "openrouter"
    assert res.model == "deepseek/deepseek-chat"
    assert "DeepSeek secondary fallback answer" in res.answer
