import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.base_model import target_metadata
from app.models import (
    User,
    Company,
    CompanyFundamentals,
    UserFollowedStock,
    KnowledgeDocument,
    DocumentChunk,
    DocumentEmbedding,
    ChatConversation,
    ChatMessage,
    InvestorMemory,
    DocumentType,
    ChatRole,
)


def test_models_and_relationships():
    tables = list(target_metadata.tables.keys())
    print("Registered SQLAlchemy Tables:")
    for t in tables:
        print(f"  - {t}")

    expected_tables = [
        "users",
        "companies",
        "company_fundamentals",
        "user_followed_stocks",
        "knowledge_documents",
        "document_chunks",
        "document_embeddings",
        "chat_conversations",
        "chat_messages",
        "investor_memory",
    ]

    missing = set(expected_tables) - set(tables)
    assert not missing, f"Missing tables in metadata: {missing}"

    # Verify ORM Relationship mapper attributes
    assert hasattr(User, "followed_stocks")
    assert hasattr(User, "chat_conversations")
    assert hasattr(User, "investor_memory")

    assert hasattr(Company, "fundamentals")
    assert hasattr(Company, "documents")
    assert hasattr(Company, "followers")

    assert hasattr(KnowledgeDocument, "company")
    assert hasattr(KnowledgeDocument, "chunks")
    assert hasattr(DocumentChunk, "embedding")

    assert hasattr(ChatConversation, "messages")

    print("\nSUCCESS: All models and bidirectional ORM relationships configured cleanly!")


if __name__ == "__main__":
    test_models_and_relationships()
