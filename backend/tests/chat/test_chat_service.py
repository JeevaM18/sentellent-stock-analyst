import sys
import os
import uuid
from unittest.mock import patch, MagicMock
import pytest  # pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.main import app
from app.db.database import SessionLocal
from app.llm.types import LLMResponse
from app.retrieval.types import RetrievalResult, RetrievalSummary
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

client = TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_chat_without_results(db):
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = RetrievalSummary(query="Random query", total=0, duration_seconds=0.0001, results=[])

    mock_gen = MagicMock()
    mock_gen.generate.return_value = LLMResponse(
        answer="I couldn't find enough evidence in the retrieved documents to answer your question.",
        model="gemini-flash-latest",
        provider="google",
        latency_ms=12.0,
    )

    req = ChatRequest(query="Random query")
    res = ChatService.ask(db=db, request=req, user_id=None, retriever_service=mock_retriever, generation_service=mock_gen)

    assert isinstance(res, ChatResponse)
    assert "I couldn't find enough evidence" in res.answer
    assert res.chunks_used == 0
    assert res.citations == []
    assert res.retrieval_time_ms >= 0.0
    assert res.total_time_ms >= res.retrieval_time_ms


def test_chat_service_ask(db):
    mock_chunk_id = uuid.uuid4()
    mock_doc_id = uuid.uuid4()
    sample_res = RetrievalResult(
        chunk_id=mock_chunk_id,
        document_id=mock_doc_id,
        company_id=None,
        ticker="RELIANCE",
        company_name="Reliance Industries",
        distance=0.15,
        similarity=0.85,
        content="Reliance Q1 revenue rose sharply.",
        chunk_index=0,
        source_title="Reliance Q1 Overview",
        source_url="https://example.com/rel",
    )

    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = RetrievalSummary(query="Reliance earnings", total=1, duration_seconds=0.0001, results=[sample_res])

    mock_gen = MagicMock()
    mock_gen.generate.return_value = LLMResponse(
        answer="Reliance Industries reported higher revenue in Q1.",
        model="gemini-flash-latest",
        provider="google",
        latency_ms=150.0,
    )

    req = ChatRequest(query="Reliance earnings", ticker="RELIANCE")
    res = ChatService.ask(db=db, request=req, user_id=None, retriever_service=mock_retriever, generation_service=mock_gen)

    assert res.answer == "Reliance Industries reported higher revenue in Q1."
    assert res.chunks_used == 1
    assert len(res.citations) == 1
    assert res.citations[0].title == "Reliance Q1 Overview"
    assert res.citations[0].ticker == "RELIANCE"
    assert res.citations[0].similarity == 0.85
    assert res.retrieval_time_ms >= 0.0
    assert res.generation_time_ms == 150.0


def test_api_chat_endpoint(db):
    conv_id = uuid.uuid4()
    mock_chat_response = ChatResponse(
        answer="Reliance Q1 performance was strong.",
        citations=[],
        chunks_used=0,
        retrieval_time_ms=10.0,
        generation_time_ms=100.0,
        total_time_ms=115.0,
        model="gemini-flash-latest",
        conversation_id=conv_id,
    )

    with patch("app.api.chat.router.ChatService.ask", return_value=mock_chat_response):
        response = client.post(
            "/api/chat",
            json={
                "query": "Why did Reliance grow?",
                "conversation_id": str(conv_id),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Reliance Q1 performance was strong."
        assert data["conversation_id"] == str(conv_id)
        assert "retrieval_time_ms" in data
        assert "generation_time_ms" in data
        assert "total_time_ms" in data
