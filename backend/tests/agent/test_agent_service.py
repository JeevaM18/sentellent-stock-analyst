import sys
import os
import uuid
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agent.service import AgentService
from app.llm.types import LLMResponse
from app.models.chat_conversation import ChatConversation
from app.retrieval.types import RetrievalResult, RetrievalSummary


def test_agent_service_retrieval_flow():
    mock_db = MagicMock()
    mock_conv_id = uuid.uuid4()
    mock_conv = ChatConversation(id=mock_conv_id, user_id=None, title="New Conversation")

    mock_result = RetrievalResult(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        company_id=uuid.uuid4(),
        ticker="INFY",
        company_name="Infosys",
        distance=0.15,
        similarity=0.85,
        content="Infosys reported solid revenue growth.",
        chunk_index=0,
        source_title="Infosys Q1 Earnings",
        source_url="https://example.com/infosys",
    )

    mock_summary = RetrievalSummary(
        query="Latest Infosys news",
        total=1,
        duration_seconds=0.045,
        results=[mock_result],
    )

    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = mock_summary

    mock_gen = MagicMock()
    mock_gen.generate.return_value = LLMResponse(
        answer="Infosys reported strong Q1 results.",
        model="gemini-flash-latest",
        provider="google",
        latency_ms=150.0,
    )

    with patch("app.services.conversation_service.ConversationService.get_conversation", return_value=mock_conv), \
         patch("app.services.conversation_service.ConversationService.create_conversation", return_value=mock_conv), \
         patch("app.services.conversation_service.ConversationService.get_messages", return_value=[]), \
         patch("app.services.conversation_service.ConversationService.append_message"), \
         patch("app.services.conversation_service.ConversationService.update_conversation_title_if_default"):

        res_state = AgentService.run(
            db=mock_db,
            question="Latest Infosys news",
            user_id=None,
            conversation_id=mock_conv_id,
            retriever_service=mock_retriever,
            generation_service=mock_gen,
        )

        assert res_state["final_answer"] == "Infosys reported strong Q1 results."
        assert "confidence" in res_state["metadata"]
        assert "reasoning" in res_state["metadata"]
        assert "retrieval" in res_state["metadata"]["tools_used"]


def test_agent_service_fundamentals_flow():
    mock_db = MagicMock()
    mock_conv_id = uuid.uuid4()
    mock_conv = ChatConversation(id=mock_conv_id, user_id=None, title="New Conversation")

    mock_gen = MagicMock()
    mock_gen.generate.return_value = LLMResponse(
        answer="Reliance PE ratio is 23.81.",
        model="gemini-flash-latest",
        provider="google",
        latency_ms=100.0,
    )

    with patch("app.services.conversation_service.ConversationService.get_conversation", return_value=mock_conv), \
         patch("app.services.conversation_service.ConversationService.create_conversation", return_value=mock_conv), \
         patch("app.services.conversation_service.ConversationService.get_messages", return_value=[]), \
         patch("app.services.conversation_service.ConversationService.append_message"), \
         patch("app.services.conversation_service.ConversationService.update_conversation_title_if_default"):

        res_state = AgentService.run(
            db=mock_db,
            question="What is Reliance PE ratio?",
            user_id=None,
            conversation_id=mock_conv_id,
            generation_service=mock_gen,
        )

        assert res_state["final_answer"] == "Reliance PE ratio is 23.81."
        assert "fundamentals" in res_state["metadata"]["tools_used"]
        assert "confidence" in res_state["metadata"]


def test_agent_service_watchlist_flow():
    mock_db = MagicMock()
    mock_conv_id = uuid.uuid4()
    mock_conv = ChatConversation(id=mock_conv_id, user_id=None, title="New Conversation")

    mock_gen = MagicMock()
    mock_gen.generate.return_value = LLMResponse(
        answer="Here is your portfolio summary.",
        model="gemini-flash-latest",
        provider="google",
        latency_ms=110.0,
    )

    with patch("app.services.conversation_service.ConversationService.get_conversation", return_value=mock_conv), \
         patch("app.services.conversation_service.ConversationService.create_conversation", return_value=mock_conv), \
         patch("app.services.conversation_service.ConversationService.get_messages", return_value=[]), \
         patch("app.services.conversation_service.ConversationService.append_message"), \
         patch("app.services.conversation_service.ConversationService.update_conversation_title_if_default"):

        res_state = AgentService.run(
            db=mock_db,
            question="Show news for my portfolio watchlist",
            user_id=None,
            conversation_id=mock_conv_id,
            generation_service=mock_gen,
        )

        assert res_state["final_answer"] == "Here is your portfolio summary."
        assert "watchlist" in res_state["metadata"]["tools_used"]
