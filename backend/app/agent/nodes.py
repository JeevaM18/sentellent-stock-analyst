import logging
import time
from typing import Any
from langchain_core.runnables import RunnableConfig

from app.agent.prompts import AGENT_SYSTEM_PROMPT
from app.agent.state import AgentState
from app.llm.service import GenerationService
from app.rag.builder import ContextBuilder
from app.rag.types import RAGContext
from app.retrieval.service import RetrieverService

logger = logging.getLogger(__name__)


def router_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    """
    Router node inspecting input state and query intent.
    Currently defaults to routing to the retrieval node.
    """
    logger.info("Agent router evaluating question: %s", state.get("question"))
    return state


def route_decision(state: AgentState) -> str:
    """Conditional router function returning target node name."""
    return "retrieve"


def retrieve_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    """
    Node executing vector similarity retrieval over knowledge documents.
    Extracts retriever and db from state['services'] or config['configurable'].
    """
    services = state.get("services", {})
    cfg = (config or {}).get("configurable", {}) if isinstance(config, dict) else {}

    db = services.get("db") or cfg.get("db")
    retriever: RetrieverService = services.get("retriever") or cfg.get("retriever") or RetrieverService()

    query = state.get("question", "")
    start_time = time.perf_counter()

    if db:
        summary = retriever.retrieve(db=db, query=query)
        rag_ctx = ContextBuilder.build(query=query, retrieval=summary, chat_history=state.get("chat_history", ""))
        retrieved_text = rag_ctx.context
        citations = [
            {
                "rank": chunk.rank,
                "title": chunk.source_title,
                "source_url": chunk.source_url,
                "ticker": chunk.ticker,
                "similarity": chunk.similarity,
            }
            for chunk in rag_ctx.chunks
        ]
        chunk_count = rag_ctx.chunk_count
    else:
        retrieved_text = ""
        citations = []
        chunk_count = 0

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Standardize tool results
    tool_results = dict(state.get("tool_results", {}))
    tool_results["retrieval"] = {
        "status": "success",
        "chunks_found": chunk_count,
        "duration_ms": duration_ms,
    }

    metadata = dict(state.get("metadata", {}))
    metadata["retrieval_time_ms"] = duration_ms

    tools_used = list(metadata.get("tools_used", []))
    if "retrieval" not in tools_used:
        tools_used.append("retrieval")
    metadata["tools_used"] = tools_used

    return {
        **state,
        "retrieved_context": retrieved_text,
        "citations": citations,
        "tool_results": tool_results,
        "metadata": metadata,
    }


def fundamentals_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    """Stub node for company financial fundamentals tool integration (Phase 7.4)."""
    return state


def watchlist_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    """Stub node for user watchlist tool integration (Phase 7.5)."""
    return state


def generate_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    """
    Node executing LLM answer generation based on prompt, chat history, and retrieved context.
    Extracts generation_service from state['services'] or config['configurable'].
    """
    services = state.get("services", {})
    cfg = (config or {}).get("configurable", {}) if isinstance(config, dict) else {}

    gen_service: GenerationService = services.get("generation_service") or cfg.get("generation_service") or GenerationService()

    start_time = time.perf_counter()

    rag_context = RAGContext(
        question=state.get("question", ""),
        system_prompt=AGENT_SYSTEM_PROMPT,
        context=state.get("retrieved_context", ""),
        chat_history=state.get("chat_history", ""),
        prompt_version="v1",
    )

    llm_resp = gen_service.generate(rag_context=rag_context)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    metadata = dict(state.get("metadata", {}))
    metadata["generation_time_ms"] = duration_ms
    metadata["model"] = llm_resp.model

    return {
        **state,
        "final_answer": llm_resp.answer,
        "metadata": metadata,
    }
