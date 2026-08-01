"""
CLI verification script for Phase 7.5, 7.6, 7.8, 7.10 & 7.11 Multi-Tool Planner & Observability.

Usage:
    cd backend
    python app/scripts/test_agent_planner.py
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agent.planner import AgentPlanner


def main():
    queries = [
        "What is Reliance PE ratio?",
        "Show news for my portfolio watchlist",
        "Compare Reliance fundamentals and today's news",
        "Why did Indian stock markets drop today?",
    ]

    print("=" * 65)
    print("Multi-Tool Planner & Explainable AI Verification")
    print("=" * 65)

    for idx, q in enumerate(queries, 1):
        plan = AgentPlanner.plan(q)
        print(f"\n[{idx}] User Question: '{q}'")
        print(f"    Planned Tools ({len(plan.tools)}):")
        for tool_call in plan.tools:
            print(f"      • Tool: {tool_call.name}")
            print(f"        Arguments: {tool_call.arguments}")

    print("\n" + "=" * 65)
    print("[OK] Multi-tool planner verification complete!")


if __name__ == "__main__":
    main()
