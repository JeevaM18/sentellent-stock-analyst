from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class ContextChunk:
    """Dataclass encapsulating a single structured chunk formatted for RAG LLM context."""
    rank: int
    chunk_id: UUID
    document_id: UUID
    company_name: str | None
    ticker: str | None
    source_title: str
    source_url: str | None
    published_at: datetime | None
    similarity: float
    content: str


@dataclass(slots=True)
class RAGContext:
    """Dataclass encapsulating the complete rendered prompt, structured chunks, and token metrics for LLM generation."""
    question: str
    system_prompt: str
    context: str
    chunks: list[ContextChunk] = field(default_factory=list)
    chunk_count: int = 0
    total_characters: int = 0
    estimated_words: int = 0
    estimated_tokens: int = 0
    prompt_version: str = "v1"
