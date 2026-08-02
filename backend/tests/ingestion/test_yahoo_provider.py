import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.ingestion.fundamentals import YahooFinanceProvider


def test_yahoo_provider_valid_stock():
    provider = YahooFinanceProvider()
    result = provider.fetch("RELIANCE")

    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["ticker"] == "RELIANCE"
    assert result["provider"] == "Yahoo Finance"
    assert "retrieved_at" in result
    assert "data" in result

    data = result["data"]
    assert "current_price" in data
    assert "market_cap" in data
    assert "pe_ratio" in data
    assert "currency" in data
    assert data["currency"] == "INR"


def test_yahoo_provider_multiple_valid_stocks():
    provider = YahooFinanceProvider()
    for ticker in ["TCS", "INFY"]:
        res = provider.fetch(ticker)
        assert res["success"] is True
        assert res["ticker"] == ticker
        assert "data" in res
        assert "market_cap" in res["data"]
        market_cap = res["data"]["market_cap"]
        assert market_cap is None or market_cap > 0


def test_yahoo_provider_invalid_stock():
    provider = YahooFinanceProvider()
    res = provider.fetch("INVALIDCOMPANY123_NON_EXISTENT")

    # Should fail gracefully with success = False without crashing
    assert isinstance(res, dict)
    assert res["success"] is False
    assert res["ticker"] == "INVALIDCOMPANY123_NON_EXISTENT"
    assert "error" in res
