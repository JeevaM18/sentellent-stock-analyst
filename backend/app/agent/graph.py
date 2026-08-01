import os
import logging
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

# Disable tracing to avoid network calls during test execution
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_TRACING"] = "false"

from app.agent.nodes import (
    executor_node,
    explainability_node,
    generate_node,
    planner_node,
)
from app.agent.state import AgentState

logger = logging.getLogger(__name__)


def create_agent_graph() -> CompiledStateGraph:
    """
    Constructs compiled LangGraph execution graph:
    START -> planner_node -> executor_node -> generate_node -> explainability_node -> END.
    """
    builder = StateGraph(AgentState)

    builder.add_node("planner", planner_node)
    builder.add_node("executor", executor_node)
    builder.add_node("generate", generate_node)
    builder.add_node("explainability", explainability_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "executor")
    builder.add_edge("executor", "generate")
    builder.add_edge("generate", "explainability")
    builder.add_edge("explainability", END)

    compiled_graph = builder.compile()
    logger.info("LangGraph AgentGraph compiled successfully (version v1)")
    return compiled_graph


class AgentGraph:
    graph: CompiledStateGraph = create_agent_graph()
    version: str = "v1"
