import os
import sys
from dotenv import load_dotenv

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

load_dotenv()

from app.db.database import SessionLocal
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService


def run_chat_cli():
    print("=" * 60)
    print("Sentellent AI — End-to-End Gemini RAG Chat CLI")
    print("=" * 60)

    db = SessionLocal()
    try:
        query_text = "Why did Reliance stock fall today?"
        request = ChatRequest(query=query_text, top_k=5)

        print(f"User Query      : {query_text}\n")
        print("Executing End-to-End RAG Pipeline (Retrieval -> Context -> Gemini LLM)...")

        chat_response = ChatService.ask(db=db, request=request)

        print("\n" + "=" * 60)
        print("AI ANSWER (Grounded Response)")
        print("=" * 60)
        print(chat_response.answer)
        print("=" * 60)

        print("\nMETRICS & EXECUTION LATENCY:")
        print(f"  Conversation ID   : {chat_response.conversation_id}")
        print(f"  Model             : {chat_response.model}")
        print(f"  Chunks Used       : {chat_response.chunks_used}")
        print(f"  Retrieval Latency : {chat_response.retrieval_time_ms:.2f} ms")
        print(f"  Generation Latency: {chat_response.generation_time_ms:.2f} ms")
        print(f"  Total Latency     : {chat_response.total_time_ms:.2f} ms")

        print("\nCITATIONS & SOURCE ATTRIBUTION:")
        if chat_response.citations:
            for c in chat_response.citations:
                print(f"  [{c.rank}] {c.title} (Ticker: {c.ticker or 'N/A'}, Similarity: {c.similarity:.4f})")
                print(f"      URL: {c.source_url or 'N/A'}")
        else:
            print("  No citations matched.")

        print("\nSUCCESS: End-to-end Sentellent AI RAG generation complete!")

    except Exception as e:
        print(f"\nChat Execution Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_chat_cli()
