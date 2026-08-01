import logging
import time
from uuid import UUID
from sqlalchemy.orm import Session

from app.chat.history import build_chat_history
from app.constants.chat import ROLE_ASSISTANT, ROLE_USER
from app.llm.constants import DEFAULT_MAX_OUTPUT_TOKENS, DEFAULT_TEMPERATURE
from app.llm.service import GenerationService
from app.rag.builder import ContextBuilder
from app.retrieval.service import RetrieverService
from app.schemas.chat import ChatRequest, ChatResponse, Citation
from app.services.conversation_service import ConversationService

logger = logging.getLogger(__name__)


class ChatService:
    """Orchestration service coordinating Retrieval, Memory History Assembly, Context Building, and Gemini LLM Generation."""

    @classmethod
    def ask(
        cls,
        *,
        db: Session,
        request: ChatRequest,
        user_id: UUID | None = None,
        retriever_service: RetrieverService | None = None,
        generation_service: GenerationService | None = None,
    ) -> ChatResponse:
        """Execute end-to-end multi-turn RAG workflow and return structured ChatResponse."""
        start_total = time.perf_counter()

        # Step 1: Manage Conversation Session & Ownership Verification
        if request.conversation_id:
            conversation = ConversationService.get_conversation(db, request.conversation_id, user_id=user_id)
            if not conversation:
                conversation = ConversationService.create_conversation(db, user_id=user_id)
        else:
            conversation = ConversationService.create_conversation(db, user_id=user_id)

        conv_id = conversation.id

        # Step 2: Fetch prior messages for History Context before appending current message
        prior_messages = ConversationService.get_messages(db, conv_id)
        chat_history_str = build_chat_history(prior_messages)

        # Step 3: Persist USER query message to Database
        ConversationService.append_message(
            db,
            conversation_id=conv_id,
            role=ROLE_USER,
            content=request.query,
        )

        # Step 4: Vector Similarity Retrieval
        retriever = retriever_service or RetrieverService()
        retrieval_summary = retriever.retrieve(
            db=db,
            query=request.query,
            top_k=request.top_k,
            company_id=request.company_id,
            ticker=request.ticker,
        )
        retrieval_time_ms = round(retrieval_summary.duration_seconds * 1000, 2)

        # Step 5: Context Building with Chat History & Token Budgeting
        rag_context = ContextBuilder.build(
            query=request.query,
            retrieval=retrieval_summary,
            chat_history=chat_history_str,
        )

        # Step 6: LLM Answer Generation
        gen_service = generation_service or GenerationService()
        temp = request.temperature if request.temperature is not None else DEFAULT_TEMPERATURE
        max_tok = request.max_output_tokens if request.max_output_tokens is not None else DEFAULT_MAX_OUTPUT_TOKENS

        llm_resp = gen_service.generate(
            rag_context=rag_context,
            temperature=temp,
            max_output_tokens=max_tok,
        )
        generation_time_ms = llm_resp.latency_ms

        # Step 7: Persist ASSISTANT answer message to Database
        ConversationService.append_message(
            db,
            conversation_id=conv_id,
            role=ROLE_ASSISTANT,
            content=llm_resp.answer,
            token_count=llm_resp.output_tokens,
            prompt_tokens=llm_resp.input_tokens,
            completion_tokens=llm_resp.output_tokens,
        )

        # Step 8: Update conversation title if default 'New Conversation'
        ConversationService.update_conversation_title_if_default(db, conversation, request.query)

        total_time_ms = round((time.perf_counter() - start_total) * 1000, 2)

        # Step 9: Build Citations List
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
            "Chat request for conversation %s completed in %.2f ms (retrieval: %.2f ms, generation: %.2f ms, chunks: %d)",
            conv_id,
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
