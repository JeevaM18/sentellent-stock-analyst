import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.db.database import SessionLocal
from app.chunking import DocumentChunker
from app.services.chunk_service import ChunkService
from app.models.knowledge_document import KnowledgeDocument


def test_chunking_cli():
    sample_text = (
        "Reliance Industries Limited (RIL) is an Indian multinational conglomerate corporate headquartered in Mumbai. "
        "It has diverse businesses including energy, petrochemicals, natural gas, retail, telecommunications, mass media, and textiles. "
        "Reliance is one of the most profitable companies in India, the largest publicly traded company in India by market capitalization, "
        "and the largest company in India as measured by revenue.\n\n"
        "Jio Platforms, a subsidiary of Reliance Industries, has revolutionized the Indian telecom sector by offering affordable 4G and 5G data services. "
        "Furthermore, Reliance Retail has expanded rapidly across tier-1, tier-2, and tier-3 Indian cities with thousands of stores nationwide. "
        "Analysts project continued earnings per share (EPS) growth driven by digital services and clean energy investments."
    )

    chunker = DocumentChunker(strategy="recursive")
    chunks = chunker.split_text(sample_text, document_title="Reliance Deep Dive Report", company_id="dummy-uuid")

    print("=" * 60)
    print(f"Characters : {len(sample_text)}")
    print(f"Chunks     : {len(chunks)}")
    print("=" * 60)

    for chunk in chunks:
        print(f"\nChunk {chunk.chunk_index}")
        print(f"Chars : {chunk.character_count} | Tokens: {chunk.token_count}")
        print(f"Hash  : {chunk.chunk_hash[:16]}...")
        print(f"Meta  : {chunk.metadata}")
        print(f"Text  : {chunk.content[:120]}...")
        print("-" * 60)

    # SQL Verification against database if any document exists
    db = SessionLocal()
    try:
        doc = db.query(KnowledgeDocument).first()
        if doc:
            print(f"\n--- Testing ChunkService.chunk_document for DB Document: '{doc.title[:30]}' ---")
            db_chunks = ChunkService.chunk_document(db, document=doc)
            print(f"Stored {len(db_chunks)} chunks in PostgreSQL for Document ID {doc.id}")
            for c in db_chunks[:3]:
                print(f"  • Index {c.chunk_index} | Chars: {c.character_count} | Tokens: {c.token_count} | Status: {c.status}")
    finally:
        db.close()


if __name__ == "__main__":
    test_chunking_cli()
