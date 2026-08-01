import sys
import os
import uuid
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.recommendation.scorer import RecommendationScorer
from app.recommendation.types import RecommendationCandidate


def test_scorer_fundamentals():
    mock_comp = MagicMock()
    mock_comp.company_name = "TCS"
    mock_comp.ticker = "TCS"
    mock_comp.exchange = "NSE"
    mock_comp.sector = "IT"

    cand = RecommendationCandidate(
        company=mock_comp,
        ticker="TCS",
        company_id=uuid.uuid4(),
        fundamentals={
            "pe_ratio": 22.5,
            "roe": 35.0,
            "debt_to_equity": 0.1,
            "eps": 115.0,
            "dividend_yield": 2.1,
            "price_to_book": 8.0,
            "beta": 0.8,
        },
    )

    result = RecommendationScorer.evaluate_candidate(cand)
    assert result.score.overall_score >= 70.0
    assert result.score.fundamental_score >= 80.0
    assert len(result.reasons) > 0
