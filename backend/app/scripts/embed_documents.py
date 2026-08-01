import argparse
import os
import sys
import logging
from dotenv import load_dotenv

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

load_dotenv()

from app.db.database import SessionLocal
from app.embeddings.constants import EMBEDDING_BATCH_SIZE
from app.embeddings.pipeline import EmbeddingPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_embedding_pipeline(limit: int = EMBEDDING_BATCH_SIZE):
    db = SessionLocal()
    try:
        pipeline = EmbeddingPipeline()
        summary = pipeline.embed_pending(db=db, limit=limit)

        print("\n" + "=" * 50)
        print("Embedding Pipeline Summary")
        print("=" * 50)
        print(f"Processed : {summary.processed}")
        print(f"Created   : {summary.created}")
        print(f"Updated   : {summary.updated}")
        print(f"Failed    : {summary.failed}")
        print(f"Duration  : {summary.duration_seconds:.2f}s")
        print("=" * 50 + "\n")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run batch vector embedding pipeline for pending document chunks.")
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=EMBEDDING_BATCH_SIZE,
        help=f"Maximum number of pending chunks to embed (default: {EMBEDDING_BATCH_SIZE})",
    )
    args = parser.parse_args()
    run_embedding_pipeline(limit=args.limit)
