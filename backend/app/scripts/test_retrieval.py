import os
import sys
from dotenv import load_dotenv

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

load_dotenv()

from app.db.database import SessionLocal
from app.retrieval.service import RetrieverService
from app.retrieval.constants import DEFAULT_MIN_SIMILARITY


def run_retrieval_cli():
    print("=" * 60)
    print("Testing Semantic Retrieval Service (pgvector)")
    print("=" * 60)

    db = SessionLocal()
    try:
        service = RetrieverService()
        query_text = "Reliance quarterly earnings and revenue growth"
        summary = service.retrieve(db=db, query=query_text, top_k=5, min_similarity=0.40)

        print(f"\nQuery        : {summary.query}")
        print(f"Total Matches: {summary.total}")
        print(f"Latency      : {summary.duration_seconds * 1000:.2f} ms")
        print("-" * 60)

        for index, res in enumerate(summary.results, start=1):
            print(f"\nResult #{index}")
            print(f"  Similarity : {res.similarity:.4f} (Distance: {res.distance:.4f})")
            print(f"  Company    : {res.company_name} ({res.ticker})")
            print(f"  Title      : {res.source_title}")
            print(f"  Chunk Index: {res.chunk_index}")
            print(f"  Source URL : {res.source_url}")
            print(f"  Content    : {res.content[:150]}...")
            print("-" * 60)

        print("\nSUCCESS: Semantic vector retrieval completed!")

    except Exception as e:
        print(f"Retrieval Execution Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_retrieval_cli()
