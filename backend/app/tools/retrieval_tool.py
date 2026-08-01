import time
import logging
from typing import Any
from sqlalchemy.orm import Session

from app.rag.builder import ContextBuilder
from app.retrieval.service import RetrieverService
from app.tools.base import BaseAgentTool

logger = logging.getLogger(__name__)


class RetrievalTool(BaseAgentTool):
    """
    Retrieval Tool executing vector similarity search over financial knowledge documents.
    """

    name = "retrieval"
    description = "Retrieves relevant financial news articles, earnings reports, and knowledge documents using vector similarity."

    def run(
        self,
        db: Session | None = None,
        retriever: RetrieverService | None = None,
        query: str = "",
        chat_history: str = "",
        top_k: int = 5,
        **kwargs: Any,
    ) -> dict[str, Any]:
        start_time = time.perf_counter()

        if not db or not query:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return self.format_output(
                tool_name=self.name,
                status="empty",
                execution_ms=duration_ms,
                formatted_context="",
                data={"chunks_found": 0},
                citations=[],
            )

        active_retriever = retriever or RetrieverService()
        summary = active_retriever.retrieve(db=db, query=query, top_k=top_k)
        rag_ctx = ContextBuilder.build(query=query, retrieval=summary, chat_history=chat_history)

        citations = [
            {
                "rank": chunk.rank,
                "title": chunk.source_title,
                "source_url": chunk.source_url,
                "ticker": chunk.ticker,
                "similarity": round(chunk.similarity, 4),
            }
            for chunk in rag_ctx.chunks
        ]

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return self.format_output(
            tool_name=self.name,
            status="success" if rag_ctx.chunk_count > 0 else "empty",
            execution_ms=duration_ms,
            formatted_context=rag_ctx.context,
            data={"chunks_found": rag_ctx.chunk_count},
            citations=citations,
        )
