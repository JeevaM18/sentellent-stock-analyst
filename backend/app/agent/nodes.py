import logging
import time
from typing import Any
from langchain_core.runnables import RunnableConfig

from app.agent.planner import AgentPlanner, ToolPlan
from app.agent.prompts import AGENT_SYSTEM_PROMPT
from app.agent.state import AgentState
from app.llm.service import GenerationService
from app.rag.types import RAGContext
from app.retrieval.service import RetrieverService
from app.tools import default_tool_registry
from app.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


def planner_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    """
    Planner node inspecting input question and creating ToolPlan specifying tool calls.
    """
    start_time = time.perf_counter()
    question = state.get("question", "")
    plan: ToolPlan = AgentPlanner.plan(question)

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info("Agent planner generated plan with %d tools: %s", len(plan.tools), [t.name for t in plan.tools])

    metadata = dict(state.get("metadata", {}))
    metadata["planner_time_ms"] = duration_ms
    metadata["tool_plan"] = plan.model_dump()
    metadata["intent"] = plan.tools[0].name if plan.tools else "retrieval"
    metadata["intent_confidence"] = 1.0

    return {
        **state,
        "metadata": metadata,
    }


def executor_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    """
    Executor node executing planned tool calls via dependency-injected ToolRegistry.
    Aggregates tool results, citations, and combined formatted context.
    """
    start_time = time.perf_counter()

    services = state.get("services", {})
    cfg = (config or {}).get("configurable", {}) if isinstance(config, dict) else {}

    db = services.get("db") or cfg.get("db")
    user_id = state.get("user_id")
    retriever: RetrieverService = services.get("retriever") or cfg.get("retriever")
    registry: ToolRegistry = services.get("registry") or cfg.get("registry") or default_tool_registry

    metadata = dict(state.get("metadata", {}))
    plan_dict = metadata.get("tool_plan", {})
    plan = ToolPlan.model_validate(plan_dict) if plan_dict else AgentPlanner.plan(state.get("question", ""))

    tool_results = dict(state.get("tool_results", {}))
    combined_contexts = []
    all_citations = list(state.get("citations", []))
    tools_used = list(metadata.get("tools_used", []))

    for tool_call in plan.tools:
        tool_name = tool_call.name
        kwargs = dict(tool_call.arguments)

        # Inject runtime dependencies
        kwargs["db"] = db
        kwargs["user_id"] = user_id
        kwargs["retriever"] = retriever
        kwargs["chat_history"] = state.get("chat_history", "")
        if "query" not in kwargs or not kwargs["query"]:
            kwargs["query"] = state.get("question", "")

        logger.info("Executor invoking tool '%s' with args %s", tool_name, kwargs)
        res = registry.execute(tool_name, **kwargs)

        tool_results[tool_name] = res
        if tool_name not in tools_used:
            tools_used.append(tool_name)

        if res.get("formatted_context"):
            combined_contexts.append(res["formatted_context"])

        if res.get("citations"):
            for c in res["citations"]:
                if c not in all_citations:
                    all_citations.append(c)

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    merged_context = "\n\n".join(combined_contexts) if combined_contexts else "No additional tool context available."

    metadata["tool_execution_ms"] = duration_ms
    metadata["tools_used"] = tools_used

    return {
        **state,
        "context": merged_context,
        "retrieved_context": merged_context,
        "citations": all_citations,
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


def explainability_node(state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    """
    Node computing empirical confidence score, explainability reasoning trace,
    and latency breakdown metadata.
    """
    citations = state.get("citations", [])
    tool_results = state.get("tool_results", {})
    metadata = dict(state.get("metadata", {}))
    tools_used = metadata.get("tools_used", [])

    # 1. Empirical Rule-Based Confidence Calculation
    confidence = 0.50  # Base confidence
    if citations:
        max_sim = max((c.get("similarity", 0.0) for c in citations), default=0.0)
        if max_sim >= 0.70:
            confidence += 0.25
        elif max_sim >= 0.40:
            confidence += 0.15

    successful_tools = [t for t, res in tool_results.items() if res.get("status") == "success"]
    if successful_tools:
        confidence += 0.15

    if state.get("context") and "No additional tool context" not in state["context"]:
        confidence += 0.05

    confidence = round(min(confidence, 0.95), 2)

    # 2. Reasoning Trace Generation
    reasoning = [
        f"Planner formulated execution plan with tools: {', '.join(tools_used)}",
    ]
    for tool_name, res in tool_results.items():
        st = res.get("status", "unknown")
        exec_ms = res.get("execution_ms", 0.0)
        reasoning.append(f"Executed tool '{tool_name}' (status: {st}, latency: {exec_ms:.2f} ms)")

    if citations:
        reasoning.append(f"Retrieved {len(citations)} supporting knowledge document chunks")

    planner_ms = metadata.get("planner_time_ms", 0.0)
    tool_ms = metadata.get("tool_execution_ms", 0.0)
    gen_ms = metadata.get("generation_time_ms", 0.0)
    total_ms = round(planner_ms + tool_ms + gen_ms, 2)

    metadata["execution_time_ms"] = total_ms
    metadata["confidence"] = confidence
    metadata["reasoning"] = reasoning

    return {
        **state,
        "metadata": metadata,
    }
