import sys
import os
from unittest.mock import MagicMock

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.tools.fundamentals import FundamentalsTool


def test_fundamentals_tool_not_found():
    tool = FundamentalsTool()
    res = tool.run(db=None, query="NonExistentTicker")
    assert res["status"] == "not_found"
    assert res["company"] is None
    assert "No company fundamental data" in res["formatted_context"]


def test_fundamentals_tool_analysis_metrics():
    # Value pricing & conservative leverage & strong ROE
    val = FundamentalsTool.analyze_valuation(pe=12.5, pb=1.2)
    lev = FundamentalsTool.analyze_leverage(de=0.3)
    prof = FundamentalsTool.analyze_profitability(roe=18.5, div_yield=2.5)

    assert "attractive P/E" in val
    assert "conservative balance sheet" in lev
    assert "Strong ROE" in prof
    assert "attractive cash returns" in prof


def test_fundamentals_tool_execution():
    mock_db = MagicMock()
    mock_company = MagicMock()
    mock_company.company_name = "Reliance Industries"
    mock_company.ticker = "RELIANCE"
    mock_company.exchange = "NSE"

    mock_fundamentals = MagicMock()
    mock_fundamentals.current_price = 1310.25
    mock_fundamentals.market_cap = 17700000000000
    mock_fundamentals.pe_ratio = 23.81
    mock_fundamentals.price_to_book = 2.10
    mock_fundamentals.eps = 55.19
    mock_fundamentals.roe = 14.20
    mock_fundamentals.debt_to_equity = 0.42
    mock_fundamentals.dividend_yield = 0.46
    mock_fundamentals.beta = 0.95
    mock_fundamentals.book_value = 620.0
    mock_fundamentals.fifty_two_week_high = 1600.0
    mock_fundamentals.fifty_two_week_low = 1100.0

    mock_company.fundamentals = mock_fundamentals
    mock_db.query().options().filter().first.return_value = mock_company

    tool = FundamentalsTool()
    res = tool.run(db=mock_db, query="Reliance")

    assert res["status"] == "success"
    assert res["company"] == "Reliance Industries"
    assert "analysis" in res
    assert "valuation" in res["analysis"]
    assert "leverage" in res["analysis"]
    assert "profitability" in res["analysis"]
    assert "Financial Reasoning Interpretations" in res["formatted_context"]
