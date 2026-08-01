import sys
import os
import uuid
from unittest.mock import patch
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.main import app

client = TestClient(app)


def test_post_agent_chat_api():
    conv_id = uuid.uuid4()
    mock_result_state = {
        "user_id": None,
        "conversation_id": conv_id,
        "question": "What is Reliance PE ratio?",
        "chat_history": "",
        "context": "Reliance PE ratio is 23.81.",
        "retrieved_context": "Reliance PE ratio is 23.81.",
        "tool_results": {
            "fundamentals": {
                "status": "success",
                "company": "Reliance",
                "execution_ms": 12.5,
                "data": {"pe_ratio": 23.81},
                "formatted_context": "PE Ratio: 23.81",
            }
        },
        "final_answer": "Reliance PE ratio is 23.81.",
        "citations": [],
        "metadata": {
            "agent_version": "v1",
            "model": "gemini-flash-latest",
            "intent": "fundamentals",
            "intent_confidence": 1.0,
            "execution_time_ms": 145.5,
            "tools_used": ["fundamentals"],
        },
        "iteration": 1,
        "services": {},
    }

    with patch("app.api.agent.router.AgentService.run", return_value=mock_result_state):
        response = client.post(
            "/api/agent/chat",
            json={"question": "What is Reliance PE ratio?"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Reliance PE ratio is 23.81."
        assert data["conversation_id"] == str(conv_id)
        assert data["intent"] == "fundamentals"
        assert data["execution_time_ms"] == 145.5
        assert data["agent_version"] == "v1"
        assert data["tools_used"] == ["fundamentals"]
        assert "fundamentals" in data["tool_results"]
