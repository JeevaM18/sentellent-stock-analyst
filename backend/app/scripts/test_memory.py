"""
CLI verification script for Phase 8 — Investor Memory (Personalized AI).

Usage:
    cd backend
    python app/scripts/test_memory.py
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.investor_memory.builder import MemoryBuilder
from app.investor_memory.extractor import MemoryExtractor
from app.investor_memory.merge import MemoryMergeEngine
from app.investor_memory.types import MemoryUpdate
from app.models.investor_memory import InvestorMemory


def main():
    print("=" * 65)
    print("Phase 8 — Investor Memory Verification & Prompt Context Generation")
    print("=" * 65)

    sample_chat_history = """
    USER: Hi, I am a moderate-risk long-term investor. I prefer Banking and IT stocks, and I avoid crypto.
    ASSISTANT: Great! I will tailor my analysis for moderate risk long-term growth in Banking and IT.
    """

    print("\n--- [1] Extracting Preferences from Chat History ---")
    extractor = MemoryExtractor()
    extraction = extractor._heuristic_extract(sample_chat_history)

    print(f"Risk Profile       : {extraction.risk_profile}")
    print(f"Investment Horizon : {extraction.investment_horizon}")
    print(f"Preferred Sectors  : {extraction.preferred_sectors}")
    print(f"Avoided Sectors    : {extraction.avoided_sectors}")
    print(f"Extraction Confid. : {extraction.confidence}")

    print("\n" + "-" * 65)
    print("--- [2] Merging Extraction into InvestorMemory Model ---")
    memory = InvestorMemory(
        preferred_sectors=[],
        avoided_sectors=[],
        memory_facts=[],
    )

    update = MemoryUpdate(extraction=extraction)
    merged_memory = MemoryMergeEngine.merge(memory, update)

    print(f"Merged Risk Profile: {merged_memory.risk_profile}")
    print(f"Merged Horizon     : {merged_memory.investment_horizon}")
    print(f"Merged Sectors     : {merged_memory.preferred_sectors}")
    print(f"Merged Avoided     : {merged_memory.avoided_sectors}")
    print(f"Empirical Confid.  : {merged_memory.confidence_score}")

    print("\n" + "-" * 65)
    print("--- [3] Generating Rendered System Prompt Context ---")
    ctx = MemoryBuilder.build(merged_memory)
    print(ctx.prompt_context)

    print("\n" + "=" * 65)
    print("[OK] Investor Memory verification complete!")


if __name__ == "__main__":
    main()
