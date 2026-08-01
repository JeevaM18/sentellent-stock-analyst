import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agent.graph import AgentGraph
from app.agent.nodes import fundamentals_node, route_decision, watchlist_node
from app.agent.state import AgentState


def test_graph_compiles():
    assert AgentGraph.version == "v1"
    assert AgentGraph.graph is not None


def test_router_defaults_to_retrieve():
    state: AgentState = {
        "user_id": None,
        "conversation_id": None,
        "question": "What is Reliance PE ratio?",
        "chat_history": "",
        "retrieved_context": "",
        "tool_results": {},
        "final_answer": "",
        "citations": [],
        "metadata": {},
        "iteration": 0,
        "services": {},
    }
    target_node = route_decision(state)
    assert target_node == "retrieve"


def test_tool_stubs_no_break():
    state: AgentState = {
        "user_id": None,
        "conversation_id": None,
        "question": "Test question",
        "chat_history": "",
        "retrieved_context": "",
        "tool_results": {},
        "final_answer": "",
        "citations": [],
        "metadata": {},
        "iteration": 0,
        "services": {},
    }
    assert fundamentals_node(state) == state
    assert watchlist_node(state) == state
