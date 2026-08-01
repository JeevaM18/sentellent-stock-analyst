import sys
import os
import uuid
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.tools.watchlist import WatchlistIntelligenceTool


def test_watchlist_tool_empty():
    tool = WatchlistIntelligenceTool()
    res = tool.run(db=None, user_id=None)
    assert res["status"] == "empty"
    assert res["data"]["count"] == 0
    assert "no followed stocks" in res["formatted_context"]


def test_watchlist_tool_execution():
    mock_db = MagicMock()
    mock_user_id = uuid.uuid4()

    mock_company = MagicMock()
    mock_company.company_name = "Reliance Industries"
    mock_company.ticker = "RELIANCE"
    mock_company.sector = "Energy"

    mock_followed = MagicMock()
    mock_followed.company = mock_company
    mock_db.query().options().filter().all.return_value = [mock_followed]

    mock_retriever = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.chunk.document.title = "Reliance Q2 Profit Surge"
    mock_chunk.chunk.document.source_url = "https://example.com/news/1"
    mock_chunk.chunk.content = "Reliance reported strong quarterly earnings."
    mock_chunk.similarity = 0.88

    mock_summary = MagicMock()
    mock_summary.results = [mock_chunk]
    mock_retriever.retrieve.return_value = mock_summary

    tool = WatchlistIntelligenceTool()
    res = tool.run(db=mock_db, user_id=mock_user_id, retriever=mock_retriever)

    assert res["status"] == "success"
    assert res["tool"] == "watchlist"
    assert res["data"]["count"] == 1
    assert "Reliance Industries" in res["formatted_context"]
    assert len(res["citations"]) == 1
    assert res["citations"][0]["ticker"] == "RELIANCE"
