import sys
import os
from unittest.mock import patch, MagicMock
import pytest  # pyrefly: ignore [missing-import]

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.embeddings.constants import EMBEDDING_DIMENSIONS
from app.embeddings.exceptions import EmbeddingProviderError
from app.embeddings.google_provider import GoogleEmbeddingProvider
from app.embeddings.types import EmbeddingResult


@patch("app.embeddings.google_provider.genai.Client")
def test_embed_text_success(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=[0.1] * EMBEDDING_DIMENSIONS)]
    mock_client.models.embed_content.return_value = mock_response

    provider = GoogleEmbeddingProvider(api_key="test-key")
    res = provider.embed_text(text="Reliance Q1 earnings report", metadata={"chunk_index": 0})

    assert isinstance(res, EmbeddingResult)
    assert res.model == "text-embedding-004"
    assert res.provider == "google"
    assert res.dimensions == 768
    assert len(res.vector) == 768
    assert res.text == "Reliance Q1 earnings report"
    assert res.metadata == {"chunk_index": 0}
    assert res.created_at is not None


def test_empty_text():
    provider = GoogleEmbeddingProvider(api_key="test-key")

    with pytest.raises(ValueError, match="Text string for embedding cannot be empty"):
        provider.embed_text(text="")

    with pytest.raises(ValueError, match="Text string for embedding cannot be empty"):
        provider.embed_text(text="   ")


@patch("app.embeddings.google_provider.genai.Client")
def test_invalid_dimension(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=[0.1] * 500)]
    mock_client.models.embed_content.return_value = mock_response

    provider = GoogleEmbeddingProvider(api_key="test-key")

    with pytest.raises(ValueError, match="Expected 768 dimensions but got 500"):
        provider.embed_text(text="Invalid dim test")


@patch("app.embeddings.google_provider.genai.Client")
def test_embed_batch(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=[0.2] * EMBEDDING_DIMENSIONS)]
    mock_client.models.embed_content.return_value = mock_response

    provider = GoogleEmbeddingProvider(api_key="test-key")
    texts = ["Text A", "Text B", "Text C"]
    results = provider.embed_batch(texts=texts)

    assert len(results) == 3
    assert [r.text for r in results] == ["Text A", "Text B", "Text C"]
    assert all(r.dimensions == 768 for r in results)


@patch("app.embeddings.google_provider.genai.Client")
def test_google_api_failure(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.models.embed_content.side_effect = Exception("API Rate Limit Exceeded")

    provider = GoogleEmbeddingProvider(api_key="test-key")

    with pytest.raises(EmbeddingProviderError, match="Google embedding API error: API Rate Limit Exceeded"):
        provider.embed_text(text="API failure test")
