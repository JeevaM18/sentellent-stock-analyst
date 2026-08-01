import sys
import os
import uuid

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.scripts.seed_companies import run_seeder

client = TestClient(app)


def test_company_seeding_and_duplicate_prevention():
    # Run seeder to populate DB
    inserted, skipped = run_seeder()
    assert (inserted + skipped) >= 90

    # Re-running seeder should skip all existing companies
    re_inserted, re_skipped = run_seeder()
    assert re_inserted == 0
    assert re_skipped >= 90


def test_list_companies_pagination():
    response = client.get("/api/companies?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] >= 90
    assert data["page"] == 1
    assert data["limit"] == 10
    assert len(data["companies"]) == 10


def test_search_companies_query():
    # 1. Search for CDSL
    res_cdsl = client.get("/api/companies?search=CDSL")
    assert res_cdsl.status_code == 200
    data_cdsl = res_cdsl.json()
    assert data_cdsl["total"] >= 1
    assert any(c["ticker"] == "CDSL" for c in data_cdsl["companies"])

    # 2. Search for CAMS
    res_cams = client.get("/api/companies?search=CAMS")
    assert res_cams.status_code == 200
    data_cams = res_cams.json()
    assert data_cams["total"] >= 1
    assert any(c["ticker"] == "CAMS" for c in data_cams["companies"])


def test_search_companies_by_sector_and_exchange():
    response = client.get("/api/companies?sector=IT&exchange=NSE")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for c in data["companies"]:
        assert c["exchange"] == "NSE"
        assert c["sector"].upper() == "IT"


def test_get_company_by_ticker():
    response = client.get("/api/companies/ticker/RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "RELIANCE"
    assert "Reliance" in data["company_name"]

    # Non-existent ticker returns 404
    res_404 = client.get("/api/companies/ticker/NON_EXISTENT_TICKER_XYZ")
    assert res_404.status_code == 404


def test_get_company_by_id():
    # First get RELIANCE UUID
    res_rel = client.get("/api/companies/ticker/RELIANCE")
    company_id = res_rel.json()["id"]

    response = client.get(f"/api/companies/{company_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == company_id
    assert data["ticker"] == "RELIANCE"

    # Non-existent UUID returns 404
    random_uuid = str(uuid.uuid4())
    res_404 = client.get(f"/api/companies/{random_uuid}")
    assert res_404.status_code == 404
