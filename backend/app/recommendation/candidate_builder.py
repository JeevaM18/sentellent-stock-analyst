import logging
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session, joinedload

from app.investor_memory.service import InvestorMemoryService
from app.models.company import Company
from app.models.user_followed_stock import UserFollowedStock
from app.recommendation.constants import MAX_CANDIDATES
from app.recommendation.types import RecommendationCandidate
from app.retrieval.service import RetrieverService

logger = logging.getLogger(__name__)


class RecommendationCandidateBuilder:
    """
    Decoupled candidate builder loading company models, fundamentals, user memory,
    watchlist status, and news articles for evaluation.
    """

    @classmethod
    def build_candidates(
        cls,
        db: Session,
        user_id: UUID | None = None,
        retriever_service: RetrieverService | None = None,
        target_sector: str | None = None,
        include_watchlist: bool = True,
        max_candidates: int = MAX_CANDIDATES,
    ) -> tuple[list[RecommendationCandidate], Any]:
        """
        Query DB for active companies, load fundamentals & user memory, fetch recent news per company.
        """
        memory = InvestorMemoryService.get_memory(db, user_id) if user_id else None

        followed_company_ids = set()
        if db and user_id and include_watchlist:
            followed_rows = db.query(UserFollowedStock.company_id).filter(UserFollowedStock.user_id == user_id).all()
            followed_company_ids = {r[0] for r in followed_rows}

        # Query companies with pre-fetched fundamentals
        query = db.query(Company).options(joinedload(Company.fundamentals))

        if target_sector:
            query = query.filter(Company.sector.ilike(f"%{target_sector}%"))

        companies = query.limit(max_candidates).all()
        retriever = retriever_service or RetrieverService()

        candidates: list[RecommendationCandidate] = []

        for comp in companies:
            f = getattr(comp, "fundamentals", None)
            fundamentals_dict = {}
            if f:
                fundamentals_dict = {
                    "current_price": float(f.current_price) if f.current_price else None,
                    "market_cap": f.market_cap,
                    "pe_ratio": float(f.pe_ratio) if f.pe_ratio else None,
                    "price_to_book": float(f.price_to_book) if f.price_to_book else None,
                    "eps": float(f.eps) if f.eps else None,
                    "roe": float(f.roe) if f.roe else None,
                    "debt_to_equity": float(f.debt_to_equity) if f.debt_to_equity else None,
                    "dividend_yield": float(f.dividend_yield) if f.dividend_yield else None,
                    "beta": float(f.beta) if f.beta else None,
                    "fifty_two_week_high": float(f.fifty_two_week_high) if f.fifty_two_week_high else None,
                    "fifty_two_week_low": float(f.fifty_two_week_low) if f.fifty_two_week_low else None,
                }

            # Fetch recent news context for candidate
            search_query = f"{comp.company_name} {comp.ticker} earnings news"
            news_items = []
            try:
                summary = retriever.retrieve(db=db, query=search_query, top_k=2)
                for chunk in summary.results:
                    news_items.append(
                        {
                            "title": chunk.source_title if hasattr(chunk, "source_title") else f"{comp.company_name} News",
                            "source_url": chunk.source_url if hasattr(chunk, "source_url") else None,
                            "similarity": round(chunk.similarity, 4),
                            "content": chunk.content[:200] if hasattr(chunk, "content") else "",
                        }
                    )
            except Exception as exc:
                logger.warning("Error fetching news chunks for candidate %s: %s", comp.ticker, exc)

            cand = RecommendationCandidate(
                company=comp,
                ticker=comp.ticker,
                company_id=comp.id,
                fundamentals=fundamentals_dict,
                retrieved_news=news_items,
                in_watchlist=comp.id in followed_company_ids,
                memory=memory,
            )
            candidates.append(cand)

        logger.info("RecommendationCandidateBuilder created %d candidates", len(candidates))
        return candidates, memory
