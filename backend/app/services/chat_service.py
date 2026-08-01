import logging
import time
from uuid import uuid4
from sqlalchemy.orm import Session

from app.llm.constants import DEFAULT_MAX_OUTPUT_TOKENS, DEFAULT_TEMPERATURE
from app.llm.service import GenerationService
from app.rag.builder import ContextBuilder
from app.retrieval.service import RetrieverService
from app.schemas.chat import ChatRequest, ChatResponse, Citation

logger = logging.getLogger(__name__)


class ChatService:
    """Orchestration service coordinating Retrieval, Context Assembly, and Gemini LLM Generation."""

    @classmethod
    def ask(
        cls,
        *,
        db: Session,
        request: ChatRequest,
        retriever_service: RetrieverService | None = None,
        generation_service: GenerationService | None = None,
    ) -> ChatResponse:
        """Execute end-to-end RAG workflow and return structured ChatResponse."""
        start_total = time.perf_counter()
        conv_id = request.conversation_id or uuid4()

        # Step 1: Vector Similarity Retrieval
        retriever = retriever_service or RetrieverService()
        retrieval_summary = retriever.retrieve(
            db=db,
            query=request.query,
            top_k=request.top_k,
            company_id=request.company_id,
            ticker=request.ticker,
        )
        retrieval_time_ms = round(retrieval_summary.duration_seconds * 1000, 2)

        # Step 2: Context Building & Token Budgeting
        rag_context = ContextBuilder.build(
            query=request.query,
            retrieval=retrieval_summary,
        )

        # Step 3: LLM Generation
        gen_service = generation_service or GenerationService()
        temp = request.temperature if request.temperature is not None else DEFAULT_TEMPERATURE
        max_tok = request.max_output_tokens if request.max_output_tokens is not None else DEFAULT_MAX_OUTPUT_TOKENS

        llm_resp = gen_service.generate(
            rag_context=rag_context,
            temperature=temp,
            max_output_tokens=max_tok,
        )
        generation_time_ms = llm_resp.latency_ms
        total_time_ms = round((time.perf_counter() - start_total) * 1000, 2)

        # Step 4: Build Citations List
        citations = [
            Citation(
                rank=chunk.rank,
                title=chunk.source_title,
                source_url=chunk.source_url,
                ticker=chunk.ticker,
                similarity=chunk.similarity,
            )
            for chunk in rag_context.chunks
        ]

        logger.info(
            "Chat request completed in %.2f ms (retrieval: %.2f ms, generation: %.2f ms, chunks: %d)",
            total_time_ms,
            retrieval_time_ms,
            generation_time_ms,
            rag_context.chunk_count,
        )

        return ChatResponse(
            answer=llm_resp.answer,
            citations=citations,
            chunks_used=rag_context.chunk_count,
            retrieval_time_ms=retrieval_time_ms,
            generation_time_ms=generation_time_ms,
            total_time_ms=total_time_ms,
            model=llm_resp.model,
            conversation_id=conv_id,
        )
