import sys
import os
import uuid
import pytest  # pyrefly: ignore [missing-import]
from fastapi import HTTPException

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.db.database import SessionLocal
from app.constants.chat import ROLE_USER, ROLE_ASSISTANT
from app.models.user import User
from app.services.conversation_service import ConversationService


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def _create_test_user(db, suffix: str = "a") -> User:
    """Helper to create a real User row in the database for FK-safe testing."""
    user = User(
        google_id=f"test_google_{uuid.uuid4().hex[:8]}_{suffix}",
        email=f"test_{uuid.uuid4().hex[:8]}_{suffix}@example.com",
        name=f"Test User {suffix.upper()}",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_create_and_get_conversation(db):
    user = _create_test_user(db, "create")
    conv = ConversationService.create_conversation(db, user_id=user.id, title="Test Session")

    assert conv.id is not None
    assert conv.user_id == user.id
    assert conv.title == "Test Session"
    assert conv.is_deleted is False

    fetched = ConversationService.get_conversation(db, conv.id, user_id=user.id)
    assert fetched is not None
    assert fetched.id == conv.id


def test_append_message(db):
    user = _create_test_user(db, "append")
    conv = ConversationService.create_conversation(db, user_id=user.id)

    msg_u = ConversationService.append_message(db, conv.id, ROLE_USER, "Hello AI")
    msg_a = ConversationService.append_message(db, conv.id, ROLE_ASSISTANT, "Hello User", token_count=10)

    messages = ConversationService.get_messages(db, conv.id)
    assert len(messages) == 2
    assert messages[0].content == "Hello AI"
    assert messages[1].content == "Hello User"
    assert messages[1].token_count == 10


def test_soft_delete_conversation(db):
    user = _create_test_user(db, "softdel")
    conv = ConversationService.create_conversation(db, user_id=user.id)

    deleted = ConversationService.soft_delete_conversation(db, conv.id, user_id=user.id)
    assert deleted is True

    fetched = ConversationService.get_conversation(db, conv.id, user_id=user.id)
    assert fetched is None


def test_cross_user_access_denied(db):
    user_a = _create_test_user(db, "owner")
    user_b = _create_test_user(db, "intruder")

    conv_a = ConversationService.create_conversation(db, user_id=user_a.id)

    with pytest.raises(HTTPException) as exc_info:
        ConversationService.get_conversation(db, conv_a.id, user_id=user_b.id)

    assert exc_info.value.status_code == 403
    assert "Access denied" in exc_info.value.detail


def test_list_user_conversations_pagination(db):
    user = _create_test_user(db, "paginate")
    for i in range(5):
        ConversationService.create_conversation(db, user_id=user.id, title=f"Chat {i}")

    conversations, total = ConversationService.list_user_conversations(db, user_id=user.id, page=1, limit=3)
    assert total == 5
    assert len(conversations) == 3
