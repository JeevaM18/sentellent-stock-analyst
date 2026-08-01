import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.recommendation.ranking import RecommendationRanker
from app.recommendation.types import RecommendationResult, RecommendationScore


def test_ranking_sorter():
    r1 = MagicMock(spec=RecommendationResult)
    r1.ticker = "RELIANCE"
    r1.score = RecommendationScore(overall_score=75.0)

    r2 = MagicMock(spec=RecommendationResult)
    r2.ticker = "TCS"
    r2.score = RecommendationScore(overall_score=92.0)

    sorted_res = RecommendationRanker.sort([r1, r2])
    assert sorted_res[0].ticker == "TCS"
    assert sorted_res[1].ticker == "RELIANCE"
