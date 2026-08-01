import sys
import os
import uuid
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.investor_memory.merge import MemoryMergeEngine
from app.investor_memory.types import MemoryExtraction, MemoryUpdate
from app.models.investor_memory import InvestorMemory


def test_memory_merge_engine():
    existing = InvestorMemory(
        user_id=uuid.uuid4(),
        risk_profile="Conservative",
        preferred_sectors=["Banking"],
        avoided_sectors=[],
        confidence_score=0.60,
    )

    extraction = MemoryExtraction(
        risk_profile="Moderate",
        investment_horizon="Long Term",
        preferred_sectors=["IT"],
        avoided_sectors=["Crypto"],
        memory_facts=["Prefers tech growth stocks"],
        confidence=0.88,
    )

    update = MemoryUpdate(extraction=extraction)
    merged = MemoryMergeEngine.merge(existing, update)

    assert merged.risk_profile == "Moderate"
    assert merged.investment_horizon == "Long Term"
    assert "Banking" in merged.preferred_sectors
    assert "IT" in merged.preferred_sectors
    assert "Crypto" in merged.avoided_sectors
    assert len(merged.memory_facts) == 1
    assert merged.confidence_score >= 0.80
