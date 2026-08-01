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
        "question": "What is TCS Q1 net profit?",
        "chat_history": "",
        "retrieved_context": "TCS net profit rose 8.7% YoY.",
        "tool_results": {"retrieval": {"status": "success", "chunks_found": 1}},
        "final_answer": "TCS net profit grew by 8.7% year-on-year.",
        "citations": [{"title": "TCS Q1 Report", "similarity": 0.88}],
        "metadata": {
            "agent_version": "v1",
            "model": "gemini-flash-latest",
            "execution_time_ms": 145.5,
            "tools_used": ["retrieval"],
        },
        "iteration": 1,
        "services": {},
    }

    with patch("app.api.agent.router.AgentService.run", return_value=mock_result_state):
        response = client.post(
            "/api/agent/chat",
            json={"question": "What is TCS Q1 net profit?"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "TCS net profit grew by 8.7% year-on-year."
        assert data["conversation_id"] == str(conv_id)
        assert data["execution_time_ms"] == 145.5
        assert data["agent_version"] == "v1"
        assert data["tools_used"] == ["retrieval"]
        assert len(data["citations"]) == 1
