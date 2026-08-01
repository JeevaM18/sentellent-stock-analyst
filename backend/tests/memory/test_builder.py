import sys
import os
import uuid
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.investor_memory.builder import MemoryBuilder


def test_memory_builder_none():
    ctx = MemoryBuilder.build(None)
    assert ctx.has_profile is False
    assert ctx.prompt_context == ""


def test_memory_builder_populated():
    mock_mem = MagicMock()
    mock_mem.risk_profile = "Moderate"
    mock_mem.investment_horizon = "Long Term"
    mock_mem.investment_style = "Growth"
    mock_mem.preferred_sectors = ["IT", "Banking"]
    mock_mem.avoided_sectors = ["Crypto"]
    mock_mem.memory_summary = "Long-term growth investor preferring Banking and IT."
    mock_mem.memory_facts = ["User prefers dividend paying stocks"]
    mock_mem.confidence_score = 0.90
    mock_mem.last_updated_from_chat = None
    mock_mem.updated_at = None

    ctx = MemoryBuilder.build(mock_mem)
    assert ctx.has_profile is True
    assert "Moderate" in ctx.prompt_context
    assert "Long Term" in ctx.prompt_context
    assert "IT, Banking" in ctx.prompt_context
    assert "Crypto" in ctx.prompt_context
    assert "Observed Investor Facts" in ctx.prompt_context
