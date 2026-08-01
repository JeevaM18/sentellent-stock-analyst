import re
from typing import Any
from pydantic import BaseModel, Field

from app.agent.intent_keywords import (
    COMBINED_KEYWORDS,
    FUNDAMENTALS_KEYWORDS,
    WATCHLIST_KEYWORDS,
)


class ToolCall(BaseModel):
    """Structured declaration of a planned tool invocation."""
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolPlan(BaseModel):
    """Structured plan specifying sequence of tool invocations to fulfill user question."""
    tools: list[ToolCall] = Field(default_factory=list)


class AgentPlanner:
    """
    Intelligent multi-tool planner inspecting question context and outputting ToolPlan.
    """

    @classmethod
    def plan(cls, question: str) -> ToolPlan:
        q = question.lower().strip()
        tokens = [t for t in re.split(r'[\s,\.\?\!]+', q) if len(t) >= 2]

        has_combined = any(kw in q for kw in COMBINED_KEYWORDS)
        has_fundamentals = any(kw in q for kw in FUNDAMENTALS_KEYWORDS)
        has_watchlist = any(kw in q for kw in WATCHLIST_KEYWORDS)

        # Detect company ticker/name token
        potential_ticker = None
        stop_words = {"what", "is", "the", "show", "me", "my", "our", "portfolio", "watchlist", "stock", "stocks", "news", "today", "latest", "compare", "and", "ratio", "price"}
        for t in tokens:
            if t not in stop_words and len(t) >= 3:
                potential_ticker = t.upper()
                break

        tools: list[ToolCall] = []

        if has_combined or (has_fundamentals and ("news" in q or "today" in q)):
            # Multi-tool planning
            tools.append(ToolCall(name="fundamentals", arguments={"query": question, "ticker": potential_ticker}))
            tools.append(ToolCall(name="retrieval", arguments={"query": question, "top_k": 5}))
        elif has_fundamentals:
            tools.append(ToolCall(name="fundamentals", arguments={"query": question, "ticker": potential_ticker}))
        elif has_watchlist:
            tools.append(ToolCall(name="watchlist", arguments={"query": question, "top_k_per_stock": 2}))
        else:
            tools.append(ToolCall(name="retrieval", arguments={"query": question, "top_k": 5}))

        return ToolPlan(tools=tools)
