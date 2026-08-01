from typing import Any
from app.recommendation.constants import (
    FUNDAMENTALS_WEIGHT,
    MEMORY_WEIGHT,
    NEWS_WEIGHT,
    PORTFOLIO_WEIGHT,
    TREND_WEIGHT,
)


def clamp_score(score: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Clamp score between min_val and max_val."""
    return round(max(min_val, min(score, max_val)), 2)


def calculate_weighted_score(
    fundamental_score: float,
    news_score: float,
    memory_score: float,
    portfolio_score: float,
    trend_score: float,
) -> float:
    """Compute overall recommendation score (0 to 100) using weighted formula."""
    weighted = (
        (fundamental_score * FUNDAMENTALS_WEIGHT)
        + (news_score * NEWS_WEIGHT)
        + (memory_score * MEMORY_WEIGHT)
        + (portfolio_score * PORTFOLIO_WEIGHT)
        + (trend_score * TREND_WEIGHT)
    )
    return clamp_score(weighted)


def risk_alignment(company_beta: float | None, risk_profile: str | None) -> float:
    """Evaluate alignment between company beta volatility and user risk profile."""
    if company_beta is None or not risk_profile:
        return 70.0  # Neutral score

    rp = risk_profile.lower()
    if "conservative" in rp:
        if company_beta <= 0.9:
            return 95.0
        elif company_beta <= 1.2:
            return 65.0
        else:
            return 35.0
    elif "aggressive" in rp:
        if company_beta >= 1.1:
            return 95.0
        else:
            return 70.0
    else:  # Moderate
        if 0.8 <= company_beta <= 1.2:
            return 90.0
        else:
            return 75.0


def sector_match(sector: str | None, preferred_sectors: list[str], avoided_sectors: list[str]) -> float:
    """Evaluate sector matching score against user investor memory."""
    if not sector:
        return 70.0

    s_clean = sector.strip().lower()

    for avoided in avoided_sectors or []:
        if avoided and avoided.strip().lower() in s_clean:
            return 0.0  # Heavy penalty for avoided sector

    for preferred in preferred_sectors or []:
        if preferred and preferred.strip().lower() in s_clean:
            return 95.0  # Strong match bonus

    return 70.0  # Neutral
