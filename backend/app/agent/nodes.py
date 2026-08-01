import re
import logging
import time
from typing import Any
from langchain_core.runnables import RunnableConfig
from sqlalchemy.orm import Session, joinedload

from app.agent.prompts import AGENT_SYSTEM_PROMPT
from app.agent.router import IntentRouter, IntentType
from app.agent.state import AgentState
from app.llm.service import GenerationService
from app.models.company import Company
from app.models.user_followed_stock import UserFollowedStock
from app.rag.builder import ContextBuilder
from app.rag.types import RAGContext
from app.retrieval.service import RetrieverService

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
    Node fetching company fundamentals metrics directly from PostgreSQL database.
    """
    services = state.get("services", {})
    cfg = (config or {}).get("configurable", {}) if isinstance(config, dict) else {}
    db: Session | None = services.get("db") or cfg.get("db")

    question = state.get("question", "")
    start_time = time.perf_counter()

    found_company: Company | None = None
    if db:
        tokens = [t for t in re.split(r'[\s,\.\?\!]+', question) if len(t) >= 2]
        for token in tokens:
            comp = (
                db.query(Company)
                .options(joinedload(Company.fundamentals))
                .filter(
                    (Company.ticker.ilike(token))
                    | (Company.company_name.ilike(f"%{token}%"))
                )
                .first()
            )
            if comp:
                found_company = comp
                break

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    tool_results = dict(state.get("tool_results", {}))

    if found_company:
        f = getattr(found_company, "fundamentals", None)
        
        # Safely extract numeric fields avoiding MagicMock formatting issues
        cp = float(f.current_price) if f and getattr(f, "current_price", None) and isinstance(f.current_price, (int, float, str)) and not isinstance(f.current_price, type) else None
        mcap = f.market_cap if f and getattr(f, "market_cap", None) else None
        pe = float(f.pe_ratio) if f and getattr(f, "pe_ratio", None) and isinstance(f.pe_ratio, (int, float, str)) else None
        eps_val = float(f.eps) if f and getattr(f, "eps", None) and isinstance(f.eps, (int, float, str)) else None
        roe_val = float(f.roe) if f and getattr(f, "roe", None) and isinstance(f.roe, (int, float, str)) else None
        dte = float(f.debt_to_equity) if f and getattr(f, "debt_to_equity", None) and isinstance(f.debt_to_equity, (int, float, str)) else None
        div = float(f.dividend_yield) if f and getattr(f, "dividend_yield", None) and isinstance(f.dividend_yield, (int, float, str)) else None
        high = float(f.fifty_two_week_high) if f and getattr(f, "fifty_two_week_high", None) and isinstance(f.fifty_two_week_high, (int, float, str)) else None
        low = float(f.fifty_two_week_low) if f and getattr(f, "fifty_two_week_low", None) and isinstance(f.fifty_two_week_low, (int, float, str)) else None

        data = {
            "company_name": str(getattr(found_company, "company_name", "N/A")),
            "ticker": str(getattr(found_company, "ticker", "N/A")),
            "exchange": str(getattr(found_company, "exchange", "NSE")),
            "current_price": cp,
            "market_cap": mcap,
            "pe_ratio": pe,
            "eps": eps_val,
            "roe": roe_val,
            "debt_to_equity": dte,
            "dividend_yield": div,
            "fifty_two_week_high": high,
            "fifty_two_week_low": low,
        }

        mcap_formatted = f"₹{mcap:,}" if isinstance(mcap, (int, float)) else f"₹{mcap}" if mcap is not None else "N/A"

        formatted_lines = [
            f"=== Company Fundamentals: {data['company_name']} ({data['ticker']}) ===",
            f"Current Price: ₹{cp}" if cp is not None else "Current Price: N/A",
            f"PE Ratio: {pe}" if pe is not None else "PE Ratio: N/A",
            f"EPS: ₹{eps_val}" if eps_val is not None else "EPS: N/A",
            f"ROE: {roe_val}%" if roe_val is not None else "ROE: N/A",
            f"Dividend Yield: {div}%" if div is not None else "Dividend Yield: N/A",
            f"Market Cap: {mcap_formatted}",
            f"52-Week High: ₹{high}" if high is not None else "52-Week High: N/A",
            f"52-Week Low: ₹{low}" if low is not None else "52-Week Low: N/A",
        ]
        formatted_context = "\n".join(formatted_lines)

        tool_results["fundamentals"] = {
            "status": "success",
            "company": data['company_name'],
            "execution_ms": duration_ms,
            "data": data,
            "formatted_context": formatted_context,
        }
    else:
        formatted_context = "No specific company fundamental metrics found in database for this question."
        tool_results["fundamentals"] = {
            "status": "not_found",
            "company": None,
            "execution_ms": duration_ms,
            "data": {},
            "formatted_context": formatted_context,
        }

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
