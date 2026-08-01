import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.investor_memory.extractor import MemoryExtractor


def test_memory_extractor_heuristic_fallback():
    extractor = MemoryExtractor()
    chat_text = "I am a moderate risk long-term investor interested in IT stocks and banking, but I avoid crypto."
    extraction = extractor._heuristic_extract(chat_text)

    assert extraction.risk_profile == "Moderate"
    assert extraction.investment_horizon == "Long Term"
    assert "IT" in extraction.preferred_sectors
    assert "Banking" in extraction.preferred_sectors
    assert "Crypto" in extraction.avoided_sectors


def test_memory_extractor_json_parser():
    extractor = MemoryExtractor()
    raw_json = """
    Here is the extracted json:
    {
      "risk_profile": "Aggressive",
      "investment_horizon": "Short Term",
      "preferred_sectors": ["Banking"],
      "avoided_sectors": ["Penny Stocks"],
      "confidence": 0.90
    }
    """
    ext = extractor.parse_json(raw_json)
    assert ext.risk_profile == "Aggressive"
    assert ext.investment_horizon == "Short Term"
    assert ext.preferred_sectors == ["Banking"]
    assert ext.confidence == 0.90
