import sys
import os
import uuid
from unittest.mock import patch, MagicMock

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.llm.types import LLMResponse
from app.models.chat_conversation import ChatConversation

client = TestClient(app)


def test_post_agent_chat_api():
    mock_conv_id = uuid.uuid4()
    mock_conv = ChatConversation(id=mock_conv_id, user_id=None, title="New Conversation")

    mock_gen = MagicMock()
    mock_gen.generate.return_value = LLMResponse(
        answer="Reliance Industries P/E ratio is currently 23.81.",
        model="gemini-flash-latest",
        provider="google",
        latency_ms=120.0,
    )

    with patch("app.services.conversation_service.ConversationService.get_conversation", return_value=mock_conv), \
         patch("app.services.conversation_service.ConversationService.create_conversation", return_value=mock_conv), \
         patch("app.services.conversation_service.ConversationService.get_messages", return_value=[]), \
         patch("app.services.conversation_service.ConversationService.append_message"), \
         patch("app.services.conversation_service.ConversationService.update_conversation_title_if_default"), \
         patch("app.agent.service.GenerationService", return_value=mock_gen), \
         patch("app.agent.nodes.GenerationService", return_value=mock_gen):

        response = client.post(
            "/api/agent/chat",
            json={"question": "What is Reliance PE ratio?"},
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        assert "conversation_id" in data
        assert data["answer"] == "Reliance Industries P/E ratio is currently 23.81."
        assert "confidence" in data
        assert "reasoning" in data
        assert "tools_used" in data
        assert "tool_results" in data
        assert "execution_time_ms" in data
