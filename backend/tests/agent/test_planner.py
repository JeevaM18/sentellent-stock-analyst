import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agent.planner import AgentPlanner, ToolPlan


def test_agent_planner_fundamentals_query():
    plan: ToolPlan = AgentPlanner.plan("What is Reliance PE ratio?")
    assert len(plan.tools) == 1
    assert plan.tools[0].name == "fundamentals"
    assert plan.tools[0].arguments["ticker"] == "RELIANCE"


def test_agent_planner_watchlist_query():
    plan: ToolPlan = AgentPlanner.plan("Show news for my portfolio watchlist")
    assert len(plan.tools) == 1
    assert plan.tools[0].name == "watchlist"


def test_agent_planner_combined_query():
    plan: ToolPlan = AgentPlanner.plan("Compare Reliance fundamentals and today's news")
    assert len(plan.tools) == 2
    tool_names = [t.name for t in plan.tools]
    assert "fundamentals" in tool_names
    assert "retrieval" in tool_names


def test_agent_planner_default_retrieval_query():
    plan: ToolPlan = AgentPlanner.plan("Why did stock markets rise today?")
    assert len(plan.tools) == 1
    assert plan.tools[0].name == "retrieval"
