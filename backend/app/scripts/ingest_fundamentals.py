import logging
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.db.database import SessionLocal
from app.ingestion.fundamentals import FundamentalsPipeline

# Configure logging for script execution
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def main():
    print("=" * 60)
    print("Fundamentals Ingestion Started")
    print("=" * 60)

    db = SessionLocal()
    try:
        summary = FundamentalsPipeline.ingest_all(db)

        print("\n" + "=" * 60)
        print("Fundamentals Ingestion Execution Summary")
        print("=" * 60)
        print(f"Processed : {summary['processed']}")
        print(f"Created   : {summary['created']}")
        print(f"Updated   : {summary['updated']}")
        print(f"Skipped   : {summary['skipped']}")
        print(f"Failed    : {summary['failed']}")
        print(f"Duration  : {summary['duration_seconds']}s")
        print("=" * 60)
    finally:
        db.close()


if __name__ == "__main__":
    main()
