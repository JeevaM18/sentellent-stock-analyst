import logging
import time
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.recommendation.builder import RecommendationContextBuilder
from app.recommendation.candidate_builder import RecommendationCandidateBuilder
from app.recommendation.constants import (
    DEFAULT_TOP_K,
    RECOMMENDATION_VERSION,
)
from app.recommendation.ranking import RecommendationRanker
from app.recommendation.scorer import RecommendationScorer
from app.recommendation.types import RecommendationResult, RecommendationSummary
from app.retrieval.service import RetrieverService

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Orchestration service running candidate collection, weighted scoring, ranking,
    and deterministic explanation generation (100% DB/Math, zero LLM credit consumption).
    """

    @classmethod
    def recommend(
        cls,
        *,
        db: Session,
        user_id: UUID | None = None,
        question: str = "Recommend top personalized stocks for my portfolio",
        top_k: int = DEFAULT_TOP_K,
        sector_filter: str | None = None,
        include_watchlist: bool = True,
        retriever_service: RetrieverService | None = None,
    ) -> dict[str, Any]:
        """Execute complete recommendation pipeline deterministically without LLM calls."""
        start_total = time.perf_counter()

        # Step 1: Collect Candidates
        start_candidates = time.perf_counter()
        candidates, memory = RecommendationCandidateBuilder.build_candidates(
            db=db,
            user_id=user_id,
            retriever_service=retriever_service,
            target_sector=sector_filter,
            include_watchlist=include_watchlist,
        )
        candidates_ms = round((time.perf_counter() - start_candidates) * 1000, 2)

        # Step 2: Score Candidates
        start_scoring = time.perf_counter()
        scored_results: list[RecommendationResult] = [
            RecommendationScorer.evaluate_candidate(cand) for cand in candidates
        ]
        scoring_ms = round((time.perf_counter() - start_scoring) * 1000, 2)

        # Step 3: Rank Candidates
        start_ranking = time.perf_counter()
        top_results = RecommendationRanker.top_k(scored_results, k=top_k, diversify_sectors=True)
        ranking_ms = round((time.perf_counter() - start_ranking) * 1000, 2)

        # Step 4: Build Context
        context_str = RecommendationContextBuilder.build_context(top_results, memory)

        # Step 5: Build Deterministic Structured Explanation (Zero LLM API Cost)
        explanation_parts = []
        for r in top_results:
            reasons_str = "; ".join([f"{reason.title}: {reason.description}" for reason in r.reasons])
            explanation_parts.append(
                f"{r.company_name} ({r.ticker}) scored {r.score.overall_score:.1f}/100 based on fundamental rating ({r.score.fundamental_score:.0f}/100) and sentiment ({r.score.news_score:.0f}/100). Key drivers: {reasons_str}."
            )

        explanation = (
            " ".join(explanation_parts)
            if explanation_parts
            else "Deterministic recommendation pipeline evaluated candidate stocks against PostgreSQL financial metrics."
        )

        total_ms = round((time.perf_counter() - start_total) * 1000, 2)

        # Collect citations
        all_citations = []
        for r in top_results:
            all_citations.extend(r.evidence.citations)

        summary = RecommendationSummary(
            total_candidates=len(candidates),
            evaluated_count=len(scored_results),
            top_k=len(top_results),
            version=RECOMMENDATION_VERSION,
            execution_time_ms=total_ms,
        )

        metadata = {
            "version": RECOMMENDATION_VERSION,
            "candidates_ms": candidates_ms,
            "scoring_ms": scoring_ms,
            "ranking_ms": ranking_ms,
            "llm_ms": 0.0,
            "total_latency_ms": total_ms,
            "candidates_evaluated": len(candidates),
        }

        logger.info(
            "Deterministic RecommendationService completed for user %s: evaluated %d candidates, returning top %d in %.2f ms (LLM Calls: 0)",
            user_id,
            len(candidates),
            len(top_results),
            total_ms,
        )

        return {
            "explanation": explanation,
            "recommendations": top_results,
            "summary": summary,
            "citations": all_citations,
            "context_str": context_str,
            "metadata": metadata,
        }
