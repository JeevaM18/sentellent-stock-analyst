import logging
import os

os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_TRACING"] = "false"

from langgraph.graph import END, START, StateGraph

from app.agent.constants import DEFAULT_AGENT_VERSION
from app.agent.nodes import (
    fundamentals_node,
    generate_node,
    retrieve_node,
    route_decision,
    router_node,
    watchlist_node,
)
from app.agent.state import AgentState

logger = logging.getLogger(__name__)


def build_agent_graph():
    """Construct and compile the LangGraph Agent StateGraph workflow with intelligent intent routing."""
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("router", router_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("fundamentals", fundamentals_node)
    workflow.add_node("watchlist", watchlist_node)
    workflow.add_node("generate", generate_node)

    # Add Edges
    workflow.add_edge(START, "router")
    
    # Conditional Edges from Router based on Intent classification
    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "retrieve": "retrieve",
            "fundamentals": "fundamentals",
            "watchlist": "watchlist",
        },
    )

    # Convergence Edges to Answer Generation Node
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("fundamentals", "generate")
    workflow.add_edge("watchlist", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()


class AgentGraph:
    """Wrapper class holding compiled agent workflow and version metadata."""

    version: str = DEFAULT_AGENT_VERSION
    graph = build_agent_graph()
