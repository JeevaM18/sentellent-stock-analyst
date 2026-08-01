import os
import sys
import uuid
from datetime import datetime, timezone
import pytest  # pyrefly: ignore [missing-import]

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.rag import ContextBuilder, RAGContext, get_system_prompt, SYSTEM_PROMPTS
from app.retrieval.types import RetrievalResult, RetrievalSummary


def test_empty_retrieval():
    summary = RetrievalSummary(query="Why did Reliance fall today?", total=0, duration_seconds=0.01, results=[])
    rag_ctx = ContextBuilder.build(query="Why did Reliance fall today?", retrieval=summary)

    assert isinstance(rag_ctx, RAGContext)
    assert rag_ctx.question == "Why did Reliance fall today?"
    assert rag_ctx.context == ""
    assert rag_ctx.chunk_count == 0
    assert rag_ctx.total_characters == 0
    assert rag_ctx.estimated_tokens == 0


def test_context_build():
    res1 = RetrievalResult(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        company_id=uuid.uuid4(),
        ticker="RELIANCE",
        company_name="Reliance Industries",
        distance=0.10,
        similarity=0.90,
        content="Reliance Industries announced strong quarterly revenue performance across digital services.",
        chunk_index=0,
        source_title="Reliance Q1 Earnings Analysis",
        source_url="https://example.com/news/1",
        published_at=datetime(2026, 7, 31, tzinfo=timezone.utc),
    )

    summary = RetrievalSummary(query="Reliance earnings", total=1, duration_seconds=0.02, results=[res1])
    rag_ctx = ContextBuilder.build(query="Reliance earnings", retrieval=summary)

    assert rag_ctx.chunk_count == 1
    assert rag_ctx.total_characters > 100
    assert rag_ctx.estimated_tokens > 10
    assert "RELIANCE" in rag_ctx.context
    assert "[Chunk 1]" in rag_ctx.context
    assert "Reliance Q1 Earnings Analysis" in rag_ctx.context
    assert rag_ctx.chunks[0].rank == 1


def test_character_limit_guard():
    # Generate 5 chunks of ~1000 characters each
    results = []
    for i in range(5):
        results.append(
            RetrievalResult(
                chunk_id=uuid.uuid4(),
                document_id=uuid.uuid4(),
                company_id=uuid.uuid4(),
                ticker="RELIANCE",
                company_name="Reliance Industries",
                distance=0.10,
                similarity=0.90,
                content="Reliance chunk content detail text line. " * 25,  # ~1000 chars each
                chunk_index=i,
                source_title=f"Report {i}",
                source_url=f"https://example.com/{i}",
            )
        )

    summary = RetrievalSummary(query="Reliance report", total=5, duration_seconds=0.05, results=results)
    # Set tight max_characters limit of 2500 chars (fits 1 block and stops before exceeding limit)
    rag_ctx = ContextBuilder.build(query="Reliance report", retrieval=summary, max_characters=2500)

    assert rag_ctx.total_characters <= 2500
    assert rag_ctx.chunk_count < 5
    assert rag_ctx.chunk_count > 0


def test_duplicate_chunks_removed():
    dup_id = uuid.uuid4()
    c1 = RetrievalResult(
        chunk_id=dup_id,
        document_id=uuid.uuid4(),
        company_id=None,
        ticker="TCS",
        company_name="TCS",
        distance=0.1,
        similarity=0.9,
        content="TCS expands cloud services contracts.",
        chunk_index=0,
        source_title="TCS Cloud Update",
        source_url="https://example.com/tcs",
    )
    c2 = RetrievalResult(
        chunk_id=dup_id,  # Duplicate chunk_id
        document_id=uuid.uuid4(),
        company_id=None,
        ticker="TCS",
        company_name="TCS",
        distance=0.1,
        similarity=0.9,
        content="TCS expands cloud services contracts.",
        chunk_index=0,
        source_title="TCS Cloud Update",
        source_url="https://example.com/tcs",
    )

    summary = RetrievalSummary(query="TCS cloud", total=2, duration_seconds=0.01, results=[c1, c2])
    rag_ctx = ContextBuilder.build(query="TCS cloud", retrieval=summary)

    assert rag_ctx.chunk_count == 1
    assert len(rag_ctx.chunks) == 1


def test_prompt_template_versioning():
    v1_prompt = get_system_prompt("v1")
    assert "Sentellent AI" in v1_prompt
    assert "v1" in SYSTEM_PROMPTS

    with pytest.raises(ValueError, match="Unknown prompt version 'v99'"):
        get_system_prompt("v99")
