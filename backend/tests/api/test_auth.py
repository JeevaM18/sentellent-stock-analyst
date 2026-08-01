import sys
import os
import uuid
from unittest.mock import patch

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_missing_authorization_header():
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert "detail" in response.json()


def test_malformed_authorization_header():
    response = client.get("/api/auth/me", headers={"Authorization": "InvalidTokenFormat"})
    assert response.status_code == 401


@patch("google.oauth2.id_token.verify_oauth2_token", side_effect=ValueError("Invalid token"))
def test_invalid_google_id_token(mock_verify):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer fake_invalid_token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Google ID Token"


@patch("google.oauth2.id_token.verify_oauth2_token")
def test_valid_google_token_auto_sync_me(mock_verify):
    test_email = f"auto_me_{uuid.uuid4()}@gmail.com"
    mock_verify.return_value = {
        "email": test_email,
        "name": "Auto Sync User",
        "picture": "https://example.com/picture.png",
    }

    # Call GET /api/auth/me with mock valid Bearer token
    headers = {"Authorization": "Bearer valid_mock_token"}
    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    assert data["email"] == test_email
    assert data["name"] == "Auto Sync User"
    assert data["profile_picture"] == "https://example.com/picture.png"
    assert "id" in data
