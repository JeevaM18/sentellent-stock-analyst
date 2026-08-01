import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agent.graph import AgentGraph, create_agent_graph
from app.agent.nodes import (
    executor_node,
    explainability_node,
    generate_node,
    planner_node,
)


def test_graph_compiles():
    graph = create_agent_graph()
    assert graph is not None
    assert AgentGraph.version == "v1"


def test_planner_node_execution():
    state = {
        "question": "Compare Reliance fundamentals and today's news",
        "metadata": {},
    }
    new_state = planner_node(state)

    assert "metadata" in new_state
    assert "tool_plan" in new_state["metadata"]
    assert new_state["metadata"]["planner_time_ms"] >= 0.0


def test_executor_and_explainability_node():
    state = {
        "question": "Show news for my portfolio watchlist",
        "user_id": None,
        "metadata": {
            "planner_time_ms": 5.0,
            "tools_used": ["watchlist"],
        },
        "tool_results": {
            "watchlist": {
                "status": "success",
                "tool": "watchlist",
                "execution_ms": 10.0,
                "formatted_context": "=== Watchlist ===",
            }
        },
        "citations": [
            {"rank": 1, "title": "News 1", "similarity": 0.85}
        ],
    }

    exp_state = explainability_node(state)
    assert exp_state["metadata"]["confidence"] >= 0.85
    assert len(exp_state["metadata"]["reasoning"]) >= 1
