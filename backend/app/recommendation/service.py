import logging
import time
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.llm.service import GenerationService
from app.rag.types import RAGContext
from app.recommendation.builder import RecommendationContextBuilder
from app.recommendation.candidate_builder import RecommendationCandidateBuilder
from app.recommendation.constants import (
    DEFAULT_RECOMMENDATION_MODEL,
    DEFAULT_TOP_K,
    RECOMMENDATION_VERSION,
)
from app.recommendation.prompts import (
    RECOMMENDATION_EXPLANATION_SYSTEM_PROMPT,
)
from app.recommendation.ranking import RecommendationRanker
from app.recommendation.scorer import RecommendationScorer
from app.recommendation.types import RecommendationResult, RecommendationSummary
from app.retrieval.service import RetrieverService

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Orchestration service running candidate collection, weighted scoring, ranking,
    context building, and grounded Gemini LLM explanation generation.
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
        generation_service: GenerationService | None = None,
    ) -> dict[str, Any]:
        """Execute complete recommendation pipeline and return structured result dict."""
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

        # Step 5: Generate LLM Explanation
        start_llm = time.perf_counter()
        gen_service = generation_service or GenerationService()
        rag_context = RAGContext(
            question=question,
            system_prompt=RECOMMENDATION_EXPLANATION_SYSTEM_PROMPT,
            context=context_str,
            chat_history="",
            prompt_version=RECOMMENDATION_VERSION,
        )
        llm_resp = gen_service.generate(rag_context=rag_context)
        llm_ms = round((time.perf_counter() - start_llm) * 1000, 2)

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
            "model": DEFAULT_RECOMMENDATION_MODEL,
            "candidates_ms": candidates_ms,
            "scoring_ms": scoring_ms,
            "ranking_ms": ranking_ms,
            "llm_ms": llm_ms,
            "total_latency_ms": total_ms,
            "candidates_evaluated": len(candidates),
        }

        logger.info(
            "RecommendationService completed for user %s: evaluated %d candidates, returning top %d in %.2f ms",
            user_id,
            len(candidates),
            len(top_results),
            total_ms,
        )

        return {
            "explanation": llm_resp.answer,
            "recommendations": top_results,
            "summary": summary,
            "citations": all_citations,
            "context_str": context_str,
            "metadata": metadata,
        }
