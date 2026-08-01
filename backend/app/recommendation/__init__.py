"""Recommendation engine package for personalized AI stock recommendations."""

from app.recommendation.builder import RecommendationContextBuilder
from app.recommendation.candidate_builder import RecommendationCandidateBuilder
from app.recommendation.ranking import RecommendationRanker
from app.recommendation.scorer import RecommendationScorer
from app.recommendation.service import RecommendationService
from app.recommendation.types import (
    RecommendationCandidate,
    RecommendationEvidence,
    RecommendationReason,
    RecommendationResult,
    RecommendationScore,
    RecommendationSummary,
)

__all__ = [
    "RecommendationContextBuilder",
    "RecommendationCandidateBuilder",
    "RecommendationRanker",
    "RecommendationScorer",
    "RecommendationService",
    "RecommendationCandidate",
    "RecommendationEvidence",
    "RecommendationReason",
    "RecommendationResult",
    "RecommendationScore",
    "RecommendationSummary",
]
