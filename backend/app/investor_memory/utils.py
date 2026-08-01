import re
from typing import Any


def normalize_sector(sector: str) -> str:
    """Normalize sector string formatting."""
    s = sector.strip()
    mapping = {
        "it": "IT",
        "tech": "IT",
        "technology": "IT",
        "software": "IT",
        "banking": "Banking",
        "banks": "Banking",
        "finance": "Financial Services",
        "financials": "Financial Services",
        "pharma": "Healthcare",
        "pharmaceuticals": "Healthcare",
        "healthcare": "Healthcare",
        "energy": "Energy",
        "oil": "Energy",
        "crypto": "Crypto",
        "cryptocurrency": "Crypto",
    }
    return mapping.get(s.lower(), s.title())


def merge_lists(existing_list: list[str] | None, new_list: list[str] | None) -> list[str]:
    """Merge two lists of strings while preserving order and removing duplicates."""
    combined = list(existing_list or [])
    for item in new_list or []:
        norm_item = normalize_sector(item) if item else ""
        if norm_item and norm_item not in combined:
            combined.append(norm_item)
    return combined


def calculate_confidence(facts_count: int, has_risk: bool, has_horizon: bool) -> float:
    """Calculate empirical confidence score for investor profile memory."""
    score = 0.50
    if has_risk:
        score += 0.20
    if has_horizon:
        score += 0.15
    if facts_count > 0:
        score += min(facts_count * 0.05, 0.15)
    return round(min(score, 0.95), 2)
