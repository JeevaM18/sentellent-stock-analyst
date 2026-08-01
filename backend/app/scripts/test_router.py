"""
CLI verification script for Phase 7.2 — IntentRouter Classification.

Usage:
    cd backend
    python app/scripts/test_router.py
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agent.router import IntentRouter


def main():
    test_queries = [
        "What is Reliance PE ratio?",
        "Show my watchlist",
        "Latest Infosys news",
        "Why did Reliance stock fall today?",
        "Compare Reliance fundamentals and summarize today's news",
        "What is TCS market cap and debt to equity?",
        "Show stocks I follow in my portfolio",
    ]

    print("=" * 60)
    print("Phase 7.2 — IntentRouter Classification Verification")
    print("=" * 60)

    for idx, q in enumerate(test_queries, 1):
        intent = IntentRouter.classify(q)
        target_node = IntentRouter.route(q)
        print(f"\n[{idx}] Question: {q}")
        print(f"    Intent     : {intent.name} ({intent.value})")
        print(f"    Target Node: {target_node}")

    print("\n" + "=" * 60)
    print("[OK] IntentRouter classification test complete!")


if __name__ == "__main__":
    main()
