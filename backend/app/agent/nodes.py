import re
import logging
import time
from typing import Any
from langchain_core.runnables import RunnableConfig
from sqlalchemy.orm import Session, joinedload

from app.agent.prompts import AGENT_SYSTEM_PROMPT
from app.agent.router import IntentRouter
from app.agent.state import AgentState
from app.llm.service import GenerationService
from app.models.user_followed_stock import UserFollowedStock
from app.rag.builder import ContextBuilder
from app.rag.types import RAGContext
from app.retrieval.service import RetrieverService
from app.tools.fundamentals import FundamentalsTool

logger = logging.getLogger(__name__)


def router_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    """
    Router node inspecting input question and classifying intent.
    Sets intent and confidence in state metadata.
    """
    question = state.get("question", "")
    intent = IntentRouter.classify(question)

    logger.info("Agent router classified question '%s' as intent: %s", question, intent.value)

    metadata = dict(state.get("metadata", {}))
    metadata["intent"] = intent.value
    metadata["intent_confidence"] = 1.0

    return {
        **state,
        "metadata": metadata,
    }


def route_decision(state: AgentState) -> str:
    """Conditional router function determining target graph branch."""
    question = state.get("question", "")
    return IntentRouter.route(question)


def retrieve_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    """
    Node executing vector similarity retrieval over knowledge documents.
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

    tool_results = dict(state.get("tool_results", {}))
    tool_results["retrieval"] = {
        "status": "success",
        "chunks_found": chunk_count,
        "execution_ms": duration_ms,
        "data": {"chunks_found": chunk_count},
        "formatted_context": retrieved_text,
    }

    metadata = dict(state.get("metadata", {}))
    metadata["retrieval_time_ms"] = duration_ms

    tools_used = list(metadata.get("tools_used", []))
    if "retrieval" not in tools_used:
        tools_used.append("retrieval")
    metadata["tools_used"] = tools_used

    return {
        **state,
        "context": retrieved_text,
        "retrieved_context": retrieved_text,
        "citations": citations,
        "tool_results": tool_results,
        "metadata": metadata,
    }


def fundamentals_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    """
    Node delegating execution to FundamentalsTool for DB lookup and financial reasoning.
    """
    services = state.get("services", {})
    cfg = (config or {}).get("configurable", {}) if isinstance(config, dict) else {}
    db: Session | None = services.get("db") or cfg.get("db")
    tool_instance: FundamentalsTool = services.get("fundamentals_tool") or FundamentalsTool()

    question = state.get("question", "")
    res = tool_instance.run(db=db, query=question)

    tool_results = dict(state.get("tool_results", {}))
    tool_results["fundamentals"] = res

    formatted_context = res.get("formatted_context", "")

    metadata = dict(state.get("metadata", {}))
    tools_used = list(metadata.get("tools_used", []))
    if "fundamentals" not in tools_used:
        tools_used.append("fundamentals")
    metadata["tools_used"] = tools_used

    return {
        **state,
        "context": formatted_context,
        "retrieved_context": formatted_context,
        "tool_results": tool_results,
        "metadata": metadata,
    }


def watchlist_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    """
    Node fetching user's followed watchlist stocks from PostgreSQL database.
    """
    services = state.get("services", {})
    cfg = (config or {}).get("configurable", {}) if isinstance(config, dict) else {}
    db: Session | None = services.get("db") or cfg.get("db")
    user_id = state.get("user_id")

    start_time = time.perf_counter()
    followed_companies = []

    if db and user_id:
        followed_rows = (
            db.query(UserFollowedStock)
            .options(joinedload(UserFollowedStock.company))
            .filter(UserFollowedStock.user_id == user_id)
            .all()
        )
        followed_companies = [r.company for r in followed_rows if getattr(r, "company", None)]

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    tool_results = dict(state.get("tool_results", {}))

    if followed_companies:
        companies_data = [
            {"ticker": str(getattr(c, "ticker", "")), "name": str(getattr(c, "company_name", "")), "sector": str(getattr(c, "sector", ""))}
            for c in followed_companies
        ]
        formatted_lines = [
            f"=== User Watchlist ({len(followed_companies)} stocks) ===",
        ]
        for c in followed_companies:
            name = getattr(c, "company_name", "")
            ticker = getattr(c, "ticker", "")
            sector = getattr(c, "sector", "N/A")
            formatted_lines.append(f"- {name} ({ticker}) [{sector or 'N/A'}]")

        formatted_context = "\n".join(formatted_lines)
        tool_results["watchlist"] = {
            "status": "success",
            "count": len(followed_companies),
            "execution_ms": duration_ms,
            "data": {"count": len(followed_companies), "companies": companies_data},
            "formatted_context": formatted_context,
        }
    else:
        formatted_context = "Your watchlist currently contains no followed stocks."
        tool_results["watchlist"] = {
            "status": "empty",
            "count": 0,
            "execution_ms": duration_ms,
            "data": {"count": 0, "companies": []},
            "formatted_context": formatted_context,
        }

    metadata = dict(state.get("metadata", {}))
    tools_used = list(metadata.get("tools_used", []))
    if "watchlist" not in tools_used:
        tools_used.append("watchlist")
    metadata["tools_used"] = tools_used

    return {
        **state,
        "context": formatted_context,
        "retrieved_context": formatted_context,
        "tool_results": tool_results,
        "metadata": metadata,
    }


def generate_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    """
    Node executing LLM answer generation based on system prompt, chat history, and active context.
    """
    services = state.get("services", {})
    cfg = (config or {}).get("configurable", {}) if isinstance(config, dict) else {}

    gen_service: GenerationService = services.get("generation_service") or cfg.get("generation_service") or GenerationService()

    start_time = time.perf_counter()

    active_context = state.get("context") or state.get("retrieved_context", "")

    rag_context = RAGContext(
        question=state.get("question", ""),
        system_prompt=AGENT_SYSTEM_PROMPT,
        context=active_context,
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
