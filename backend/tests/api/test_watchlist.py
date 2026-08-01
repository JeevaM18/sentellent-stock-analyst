import sys
import os
import uuid
from unittest.mock import patch

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.scripts.seed_companies import run_seeder

client = TestClient(app)


def test_watchlist_authentication_required():
    # Requests without Bearer header return 401 Unauthorized
    res_follow = client.post("/api/watchlist/follow", json={"company_id": str(uuid.uuid4())})
    assert res_follow.status_code == 401

    res_list = client.get("/api/watchlist")
    assert res_list.status_code == 401

    res_count = client.get("/api/watchlist/count")
    assert res_count.status_code == 401


@patch("app.core.security.id_token.verify_oauth2_token")
def test_watchlist_full_crud_flow(mock_verify):
    # Ensure companies are seeded
    run_seeder()

    # Mock user identity
    test_user_email = f"watchlist_test_{uuid.uuid4()}@gmail.com"
    mock_verify.return_value = {
        "email": test_user_email,
        "name": "Watchlist Tester",
        "picture": "https://example.com/avatar.png",
    }
    headers = {"Authorization": "Bearer valid_test_token"}

    # Get sample companies: RELIANCE & TCS
    res_rel = client.get("/api/companies/ticker/RELIANCE")
    assert res_rel.status_code == 200
    rel_id = res_rel.json()["id"]

    res_tcs = client.get("/api/companies/ticker/TCS")
    assert res_tcs.status_code == 200
    tcs_id = res_tcs.json()["id"]

    # 1. Initial Check -> following = False
    res_check_rel = client.get(f"/api/watchlist/check/{rel_id}", headers=headers)
    assert res_check_rel.status_code == 200
    assert res_check_rel.json()["following"] is False

    # 2. Follow RELIANCE -> 201 Created
    res_follow_rel = client.post("/api/watchlist/follow", json={"company_id": rel_id}, headers=headers)
    assert res_follow_rel.status_code == 201
    rel_item = res_follow_rel.json()["watchlist_item"]
    assert rel_item["company_id"] == rel_id
    assert rel_item["ticker"] == "RELIANCE"
    assert rel_item["following"] is True

    # 3. Duplicate Follow RELIANCE -> 409 Conflict
    res_dup = client.post("/api/watchlist/follow", json={"company_id": rel_id}, headers=headers)
    assert res_dup.status_code == 409

    # 4. Follow TCS -> 201 Created
    res_follow_tcs = client.post("/api/watchlist/follow", json={"company_id": tcs_id}, headers=headers)
    assert res_follow_tcs.status_code == 201

    # 5. List Watchlist -> ordered by followed_at DESC (TCS first, then RELIANCE)
    res_list = client.get("/api/watchlist", headers=headers)
    assert res_list.status_code == 200
    items = res_list.json()["items"]
    assert len(items) == 2
    assert items[0]["company_id"] == tcs_id
    assert items[1]["company_id"] == rel_id

    # 6. Watchlist Count -> 2
    res_count = client.get("/api/watchlist/count", headers=headers)
    assert res_count.status_code == 200
    assert res_count.json()["count"] == 2

    # 7. Check RELIANCE following status -> True
    res_check_after = client.get(f"/api/watchlist/check/{rel_id}", headers=headers)
    assert res_check_after.status_code == 200
    assert res_check_after.json()["following"] is True

    # 8. Unfollow RELIANCE -> 200 OK
    res_unfollow = client.delete(f"/api/watchlist/unfollow/{rel_id}", headers=headers)
    assert res_unfollow.status_code == 200
    assert res_unfollow.json()["message"] == "Company unfollowed successfully"

    # 9. Check RELIANCE following status after unfollow -> False
    res_check_unfollowed = client.get(f"/api/watchlist/check/{rel_id}", headers=headers)
    assert res_check_unfollowed.status_code == 200
    assert res_check_unfollowed.json()["following"] is False

    # 10. Unfollow non-existent or un-followed -> 404 Not Found
    res_unfollow_404 = client.delete(f"/api/watchlist/unfollow/{rel_id}", headers=headers)
    assert res_unfollow_404.status_code == 404

    # 11. Follow non-existent UUID -> 404 Not Found
    fake_uuid = str(uuid.uuid4())
    res_fake = client.post("/api/watchlist/follow", json={"company_id": fake_uuid}, headers=headers)
    assert res_fake.status_code == 404
