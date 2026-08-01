import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.dependencies.current_user import get_optional_current_user
from app.models.user import User
from app.recommendation.schemas import (
    RecommendationItemSchema,
    RecommendationReasonSchema,
    RecommendationRequest,
    RecommendationResponse,
)
from app.recommendation.service import RecommendationService

logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse)
def get_stock_recommendations(
    payload: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """
    POST /api/recommendations
    Computes personalized stock recommendations deterministically via weighted scoring,
    ranked by RecommendationRanker, and explained by Gemini LLM.
    """
    try:
        user_id = current_user.id if current_user else None

        res = RecommendationService.recommend(
            db=db,
            user_id=user_id,
            top_k=min(payload.top_k, 10),
            sector_filter=payload.sector,
            include_watchlist=payload.include_watchlist,
        )

        recommendation_items = []
        for r in res.get("recommendations", []):
            reasons_schema = [
                RecommendationReasonSchema(
                    title=reason.title,
                    description=reason.description,
                    category=reason.category,
                )
                for reason in r.reasons
            ]
            recommendation_items.append(
                RecommendationItemSchema(
                    company_name=r.company_name,
                    ticker=r.ticker,
                    exchange=r.exchange,
                    overall_score=r.score.overall_score,
                    confidence=r.score.confidence,
                    fundamental_score=r.score.fundamental_score,
                    news_score=r.score.news_score,
                    memory_score=r.score.memory_score,
                    portfolio_score=r.score.portfolio_score,
                    trend_score=r.score.trend_score,
                    reasons=reasons_schema,
                    risk_level=r.risk_level,
                    expected_horizon=r.expected_horizon,
                )
            )

        summary = res.get("summary")
        total_candidates = summary.total_candidates if summary else len(recommendation_items)
        exec_ms = summary.execution_time_ms if summary else 0.0

        return RecommendationResponse(
            explanation=res.get("explanation", ""),
            recommendations=recommendation_items,
            total_candidates=total_candidates,
            execution_time_ms=exec_ms,
            confidence=recommendation_items[0].confidence if recommendation_items else 0.85,
            citations=res.get("citations", []),
            metadata=res.get("metadata", {}),
        )

    except Exception as exc:
        logger.error("Error executing /api/recommendations endpoint: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {exc}",
        ) from exc
