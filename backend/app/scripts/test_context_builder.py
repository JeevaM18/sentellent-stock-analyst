import os
import sys
from dotenv import load_dotenv

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

load_dotenv()

from app.db.database import SessionLocal
from app.retrieval.service import RetrieverService
from app.rag.builder import ContextBuilder


def run_context_builder_cli():
    print("=" * 60)
    print("Testing RAG ContextBuilder & Prompt Assembly")
    print("=" * 60)

    db = SessionLocal()
    try:
        query_text = "Why did Reliance stock fall?"
        retriever = RetrieverService()
        retrieval_summary = retriever.retrieve(db=db, query=query_text, top_k=5, min_similarity=0.40)

        rag_ctx = ContextBuilder.build(query=query_text, retrieval=retrieval_summary)

        print(f"\nQuestion        : {rag_ctx.question}")
        print(f"Chunks Used     : {rag_ctx.chunk_count}")
        print(f"Total Characters: {rag_ctx.total_characters}")
        print(f"Estimated Words : {rag_ctx.estimated_words}")
        print(f"Estimated Tokens: {rag_ctx.estimated_tokens}")
        print(f"Prompt Version  : {rag_ctx.prompt_version}")
        print("-" * 60)
        print("System Prompt Preview:")
        print(f"{rag_ctx.system_prompt[:250]}...")
        print("-" * 60)
        print("Rendered Prompt Context:")
        print(rag_ctx.context[:600] if rag_ctx.context else "[No Context Chunks Matched]")
        print("=" * 60)
        print("Ready for Gemini LLM Generation: YES")

    except Exception as e:
        print(f"ContextBuilder Execution Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_context_builder_cli()
