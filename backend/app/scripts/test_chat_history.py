"""
CLI verification script for Phase 6.4 — Multi-turn Conversation Memory.
Performs a 2-turn RAG chat conversation testing memory retention across turns.

Usage:
    cd backend
    python app/scripts/test_chat_history.py
"""
import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from app.db.database import SessionLocal
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService


def main():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Phase 6.4 — Multi-Turn Conversation Memory Verification")
        print("=" * 60)

        # --- Turn 1 ---
        print("\n--- Turn 1 ---")
        q1 = "How did Reliance perform in Q1 2026?"
        print(f"USER: {q1}")

        req1 = ChatRequest(query=q1)
        res1 = ChatService.ask(db=db, request=req1, user_id=None)

        print(f"\nASSISTANT: {res1.answer[:200]}...")
        print(f"Conversation ID: {res1.conversation_id}")
        print(f"Chunks Used: {res1.chunks_used}")
        print(f"Retrieval: {res1.retrieval_time_ms:.2f} ms")
        print(f"Generation: {res1.generation_time_ms:.2f} ms")
        print(f"Total: {res1.total_time_ms:.2f} ms")

        # --- Turn 2 (same conversation) ---
        print("\n--- Turn 2 (same conversation) ---")
        q2 = "What about their digital services segment?"
        print(f"USER: {q2}")

        req2 = ChatRequest(query=q2, conversation_id=res1.conversation_id)
        res2 = ChatService.ask(db=db, request=req2, user_id=None)

        print(f"\nASSISTANT: {res2.answer[:200]}...")
        print(f"Conversation ID: {res2.conversation_id}")
        print(f"Chunks Used: {res2.chunks_used}")
        print(f"Retrieval: {res2.retrieval_time_ms:.2f} ms")
        print(f"Generation: {res2.generation_time_ms:.2f} ms")
        print(f"Total: {res2.total_time_ms:.2f} ms")

        # --- Verify stored conversation history ---
        print("\n" + "=" * 60)
        print("Conversation History Verification")
        print("=" * 60)
        conv = ConversationService.get_conversation(db, res1.conversation_id)
        if conv:
            print(f"Title: {conv.title}")
            print(f"Last Message At: {conv.last_message_at}")

            messages = ConversationService.get_messages(db, conv.id)
            print(f"Total Messages Stored: {len(messages)}")
            for msg in messages:
                role_tag = msg.role.ljust(10)
                snippet = msg.content[:80].replace("\n", " ")
                print(f"  [{role_tag}] {snippet}...")
        else:
            print("ERROR: Conversation not found in database!")

        print("\n✅ Multi-turn conversation memory verification complete!")

    except Exception as exc:
        logger.error("CLI verification failed: %s", exc, exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    main()
