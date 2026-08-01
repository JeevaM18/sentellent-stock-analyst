import time
import logging
from typing import Any
from sqlalchemy.orm import Session

from app.recommendation.service import RecommendationService
from app.tools.base import BaseAgentTool

logger = logging.getLogger(__name__)


class RecommendationTool(BaseAgentTool):
    """
    Recommendation Tool executing deterministic weighted scoring and generating
    personalized stock recommendations grounded in investor memory, news, and fundamentals.
    """

    name = "recommendation"
    description = "Generates personalized stock recommendations matching investor profile memory, fundamentals, and recent news."

    def run(
        self,
        db: Session | None = None,
        user_id: Any = None,
        query: str = "Recommend top stocks for my portfolio",
        top_k: int = 5,
        sector: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        start_time = time.perf_counter()

        if not db:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return self.format_output(
                tool_name=self.name,
                status="empty",
                execution_ms=duration_ms,
                formatted_context="Database session is required to execute recommendation scoring engine.",
                data={"recommendations": []},
            )

        res = RecommendationService.recommend(
            db=db,
            user_id=user_id,
            question=query,
            top_k=top_k,
            sector_filter=sector,
        )

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        rec_items = [
            {
                "ticker": r.ticker,
                "company_name": r.company_name,
                "score": r.score.overall_score,
                "reasons": [reason.title for reason in r.reasons[:3]],
            }
            for r in res.get("recommendations", [])
        ]

        return self.format_output(
            tool_name=self.name,
            status="success" if rec_items else "empty",
            execution_ms=duration_ms,
            formatted_context=res.get("context_str", ""),
            data={"count": len(rec_items), "recommendations": rec_items},
            citations=res.get("citations", []),
        )

    def recommend_sector(self, db: Session, user_id: Any, sector: str, top_k: int = 5) -> dict[str, Any]:
        """Convenience method for sector-filtered recommendations."""
        return self.run(db=db, user_id=user_id, query=f"Recommend top {sector} stocks", sector=sector, top_k=top_k)

    def recommend_dividend(self, db: Session, user_id: Any, top_k: int = 5) -> dict[str, Any]:
        """Convenience method for dividend stock recommendations."""
        return self.run(db=db, user_id=user_id, query="Recommend top high dividend yield stocks", top_k=top_k)

    def recommend_growth(self, db: Session, user_id: Any, top_k: int = 5) -> dict[str, Any]:
        """Convenience method for growth stock recommendations."""
        return self.run(db=db, user_id=user_id, query="Recommend top high growth stocks", top_k=top_k)
