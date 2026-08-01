import sys
import os
import uuid
from datetime import datetime, timezone
import pytest  # pyrefly: ignore [missing-import]

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.chat.history import build_chat_history
from app.constants.chat import ROLE_ASSISTANT, ROLE_USER
from app.models.chat_message import ChatMessage


def test_build_chat_history_empty():
    assert build_chat_history([]) == ""


def test_build_chat_history_exchanges():
    conv_id = uuid.uuid4()
    msg1 = ChatMessage(id=uuid.uuid4(), conversation_id=conv_id, role=ROLE_USER, content="How did Reliance perform?", created_at=datetime.now(timezone.utc))
    msg2 = ChatMessage(id=uuid.uuid4(), conversation_id=conv_id, role=ROLE_ASSISTANT, content="Reliance reported Q1 revenue growth.", created_at=datetime.now(timezone.utc))

    history_str = build_chat_history([msg1, msg2])
    assert "USER: How did Reliance perform?" in history_str
    assert "ASSISTANT: Reliance reported Q1 revenue growth." in history_str


def test_build_chat_history_truncation():
    conv_id = uuid.uuid4()
    messages = []
    for i in range(15):
        messages.append(ChatMessage(id=uuid.uuid4(), conversation_id=conv_id, role=ROLE_USER, content=f"Question {i}", created_at=datetime.now(timezone.utc)))
        messages.append(ChatMessage(id=uuid.uuid4(), conversation_id=conv_id, role=ROLE_ASSISTANT, content=f"Answer {i}", created_at=datetime.now(timezone.utc)))

    history_str = build_chat_history(messages, max_exchanges=10)
    lines = history_str.split("\n")
    assert len(lines) == 20  # 10 exchanges * 2 lines per exchange
    assert "USER: Question 5" in history_str
    assert "USER: Question 0" not in history_str
