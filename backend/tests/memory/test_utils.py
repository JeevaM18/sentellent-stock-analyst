import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.investor_memory.utils import calculate_confidence, merge_lists, normalize_sector


def test_normalize_sector():
    assert normalize_sector("it") == "IT"
    assert normalize_sector("tech") == "IT"
    assert normalize_sector("banking") == "Banking"
    assert normalize_sector("crypto") == "Crypto"
    assert normalize_sector("Energy") == "Energy"


def test_merge_lists():
    existing = ["IT", "Banking"]
    new_items = ["banking", "Energy", "Crypto"]
    merged = merge_lists(existing, new_items)

    assert "IT" in merged
    assert "Banking" in merged
    assert "Energy" in merged
    assert "Crypto" in merged
    assert len(merged) == 4


def test_calculate_confidence():
    c1 = calculate_confidence(facts_count=0, has_risk=False, has_horizon=False)
    assert c1 == 0.50

    c2 = calculate_confidence(facts_count=2, has_risk=True, has_horizon=True)
    assert c2 >= 0.85
