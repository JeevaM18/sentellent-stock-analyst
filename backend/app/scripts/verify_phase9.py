"""Quick verification script for Phase 9 final checks."""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

print("=" * 65)
print("Phase 9 -- Final Verification Checks")
print("=" * 65)

# Check 2: Agent Planner routes recommendation intent
print("\n--- [Check 2] Agent Planner Integration ---")
from app.agent.planner import AgentPlanner

plan = AgentPlanner.plan("Recommend a long-term IT stock.")
print("Question: 'Recommend a long-term IT stock.'")
print("Planned tools: %s" % [t.name for t in plan.tools])
assert plan.tools[0].name == "recommendation", "Expected recommendation tool"
print("[PASS] Planner correctly routes to RecommendationTool")

# Check 3: ToolRegistry.list_tools()
print("\n--- [Check 3] ToolRegistry.list_tools() ---")
from app.tools import default_tool_registry

registered = default_tool_registry.list_tools()
print("Registered tools: %s" % registered)
expected = {"retrieval", "fundamentals", "watchlist", "memory", "recommendation"}
assert expected.issubset(set(registered)), "Missing tools"
print("[PASS] All 5 tools registered in ToolRegistry")

print("\n" + "=" * 65)
print("[OK] All Phase 9 verification checks passed!")
print("=" * 65)
