"""
CLI verification script for Phase 7.1 — LangGraph Agent Architecture.

Usage:
    cd backend
    python app/scripts/test_agent.py
"""
import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from app.agent.service import AgentService
from app.db.database import SessionLocal


def main():
    db = SessionLocal()
    try:
        question = "Why did Reliance stock fall today?"
        print("=" * 60)
        print("Sentellent AI Financial Agent (LangGraph v1)")
        print("=" * 60)
        print(f"\nQuestion:\n  {question}")

        result_state = AgentService.run(
            db=db,
            question=question,
            user_id=None,
        )

        metadata = result_state.get("metadata", {})
        tools_used = metadata.get("tools_used", [])
        exec_time = metadata.get("execution_time_ms", 0.0)
        citations = result_state.get("citations", [])
        answer = result_state.get("final_answer", "")

        print("\n" + "-" * 60)
        print("Tools Used:")
        for t in tools_used:
            print(f"  - {t}")

        print("\n" + "-" * 60)
        print(f"Execution Time:\n  {exec_time:.2f} ms")

        print("\n" + "-" * 60)
        print("Citations:")
        if citations:
            for idx, c in enumerate(citations, 1):
                sim = c.get("similarity", 0.0)
                title = c.get("title", "N/A")
                print(f"  [{idx}] {title} (Similarity: {sim:.4f})")
        else:
            print("  No citations retrieved.")

        print("\n" + "-" * 60)
        print(f"Answer:\n{answer}")

        print("\n" + "=" * 60)
        print("Conversation Session ID:")
        print(f"  {result_state.get('conversation_id')}")
        print("=" * 60)
        print("✅ LangGraph Agent workflow execution complete!")

    except Exception as exc:
        logger.error("CLI agent verification failed: %s", exc, exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    main()
