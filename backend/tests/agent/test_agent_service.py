import sys
import os
import uuid
from unittest.mock import MagicMock, patch
import pytest  # pyrefly: ignore [missing-import]

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agent.service import AgentService
from app.llm.types import LLMResponse
from app.models.chat_conversation import ChatConversation
from app.retrieval.types import RetrievalSummary


def test_agent_service_run():
    mock_db = MagicMock()
    mock_conv_id = uuid.uuid4()
    mock_conv = ChatConversation(id=mock_conv_id, user_id=None, title="New Conversation")

    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = RetrievalSummary(
        query="Why did Reliance stock fall?",
        total=0,
        duration_seconds=0.0001,
        results=[],
    )

    mock_gen = MagicMock()
    mock_gen.generate.return_value = LLMResponse(
        answer="Reliance stock dipped due to broader market profit booking.",
        model="gemini-flash-latest",
        provider="google",
        latency_ms=120.0,
    )

    with patch("app.services.conversation_service.ConversationService.get_conversation", return_value=mock_conv), \
         patch("app.services.conversation_service.ConversationService.create_conversation", return_value=mock_conv), \
         patch("app.services.conversation_service.ConversationService.get_messages", return_value=[]), \
         patch("app.services.conversation_service.ConversationService.append_message"), \
         patch("app.services.conversation_service.ConversationService.update_conversation_title_if_default"):

        res_state = AgentService.run(
            db=mock_db,
            question="Why did Reliance stock fall?",
            user_id=None,
            conversation_id=mock_conv_id,
            retriever_service=mock_retriever,
            generation_service=mock_gen,
        )

        assert res_state["question"] == "Why did Reliance stock fall?"
        assert res_state["final_answer"] == "Reliance stock dipped due to broader market profit booking."
        assert res_state["conversation_id"] == mock_conv_id
        assert "retrieval" in res_state["metadata"]["tools_used"]
        assert res_state["metadata"]["execution_time_ms"] >= 0.0
