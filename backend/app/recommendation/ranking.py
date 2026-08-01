import logging
from app.recommendation.constants import MIN_RECOMMENDATION_SCORE
from app.recommendation.types import RecommendationResult

logger = logging.getLogger(__name__)


class RecommendationRanker:
    """
    Ranks, filters, and diversifies recommendation results.
    """

    @classmethod
    def sort(cls, results: list[RecommendationResult]) -> list[RecommendationResult]:
        """Sort recommendation results descending by overall score."""
        return sorted(results, key=lambda r: r.score.overall_score, reverse=True)

    @classmethod
    def filter(
        cls,
        results: list[RecommendationResult],
        min_score: float = MIN_RECOMMENDATION_SCORE,
    ) -> list[RecommendationResult]:
        """Filter out low-scoring candidates."""
        return [r for r in results if r.score.overall_score >= min_score]

    @classmethod
    def remove_duplicates(cls, results: list[RecommendationResult]) -> list[RecommendationResult]:
        """Deduplicate recommendation candidates by ticker."""
        seen = set()
        unique = []
        for r in results:
            if r.ticker not in seen:
                seen.add(r.ticker)
                unique.append(r)
        return unique

    @classmethod
    def group_by_sector(cls, results: list[RecommendationResult], max_per_sector: int = 2) -> list[RecommendationResult]:
        """Prevent single-sector concentration by capping maximum recommendations per sector."""
        sector_counts: dict[str, int] = {}
        diversified = []

        for r in results:
            # Extract sector or default
            sec = getattr(r, "sector", "General")
            count = sector_counts.get(sec, 0)
            if count < max_per_sector:
                diversified.append(r)
                sector_counts[sec] = count + 1

        return diversified

    @classmethod
    def top_k(
        cls,
        results: list[RecommendationResult],
        k: int = 5,
        diversify_sectors: bool = True,
    ) -> list[RecommendationResult]:
        """Apply sorting, filtering, deduplication, sector diversification, and top_k slice."""
        filtered = cls.filter(results)
        unique = cls.remove_duplicates(filtered)
        sorted_results = cls.sort(unique)

        if diversify_sectors:
            diversified = cls.group_by_sector(sorted_results, max_per_sector=2)
            return diversified[:k]

        return sorted_results[:k]
