from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
from typing import Any
import tiktoken

from app.chunking.factory import ChunkerFactory
from app.constants.chunks import CHUNK_STATUS_NEW, TOKENIZER_ENCODING
from app.models.knowledge_document import KnowledgeDocument


@dataclass
class ChunkData:
    """Dataclass holding normalized chunk metadata and content."""
    chunk_index: int
    content: str
    chunk_hash: str
    token_count: int
    character_count: int
    start_char: int
    end_char: int
    status: str
    embedding_model: str | None
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DocumentChunker:
    """Splits raw text and KnowledgeDocument records into semantic, token-counted chunks."""

    def __init__(self, strategy: str = "recursive"):
        self.splitter = ChunkerFactory.create(strategy)
        self.encoding = tiktoken.get_encoding(TOKENIZER_ENCODING)

    def split_text(
        self,
        text: str,
        document_title: str | None = None,
        company_id: str | None = None,
    ) -> list[ChunkData]:
        if not text or not text.strip():
            return []

        chunks = self.splitter.split_text(text)
        results: list[ChunkData] = []
        cursor = 0

        for index, chunk in enumerate(chunks):
            start = text.find(chunk, cursor)
            if start == -1:
                start = cursor

            end = start + len(chunk)
            cursor = max(cursor, start + 1)

            c_hash = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
            t_count = len(self.encoding.encode(chunk))
            c_count = len(chunk)

            meta = {
                "chunk_index": index,
                "start_char": start,
                "end_char": end,
                "document_title": document_title,
                "company_id": company_id,
            }

            results.append(
                ChunkData(
                    chunk_index=index,
                    content=chunk,
                    chunk_hash=c_hash,
                    token_count=t_count,
                    character_count=c_count,
                    start_char=start,
                    end_char=end,
                    status=CHUNK_STATUS_NEW,
                    embedding_model=None,
                    metadata=meta,
                )
            )

        return results

    def split_document(
        self,
        document: KnowledgeDocument,
    ) -> list[ChunkData]:
        return self.split_text(
            text=document.content,
            document_title=document.title,
            company_id=str(document.company_id) if document.company_id else None,
        )
