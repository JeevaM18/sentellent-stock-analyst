import sys
import os
from unittest.mock import patch, MagicMock
import pytest  # pyrefly: ignore [missing-import]

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.llm.google_provider import GoogleLLMProvider
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
    assert res.model == "gemini-flash-latest"
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


@patch("app.llm.google_provider.genai.Client")
def test_provider_failure(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.models.generate_content.side_effect = Exception("API Connection Timeout")

    provider = GoogleLLMProvider(api_key="test-key")
    ctx = RAGContext(question="Fail test", system_prompt="Sys", context="Ctx", chunks=[])

    with pytest.raises(RuntimeError, match="Google Gemini generation error: API Connection Timeout"):
        provider.generate(rag_context=ctx)
