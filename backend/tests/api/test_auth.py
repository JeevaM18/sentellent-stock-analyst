import sys
import os
import uuid

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_user_sync_flow():
    # Use random UUID email to ensure 100% test isolation across multiple test runs
    test_email = f"test-{uuid.uuid4()}@gmail.com"

    test_payload = {
        "email": test_email,
        "name": "Jeeva Sync Test",
        "picture": "https://example.com/jeeva.png",
    }

    # 1. Initial Sync -> User Creation (created = True)
    response = client.post("/api/auth/sync", json=test_payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    assert data["email"] == test_payload["email"]
    assert data["name"] == test_payload["name"]
    assert data["profile_picture"] == test_payload["picture"]
    assert data["created"] is True
    assert "id" in data

    # 2. Repeat Sync -> User Update (created = False)
    updated_payload = {
        "email": test_email,
        "name": "Jeeva Sync Updated",
        "picture": "https://example.com/jeeva_new.png",
    }

    response_repeat = client.post("/api/auth/sync", json=updated_payload)
    assert response_repeat.status_code == 200
    data_repeat = response_repeat.json()

    assert data_repeat["email"] == updated_payload["email"]
    assert data_repeat["name"] == updated_payload["name"]
    assert data_repeat["profile_picture"] == updated_payload["picture"]
    assert data_repeat["created"] is False
    assert data_repeat["id"] == data["id"]
