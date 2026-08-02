import logging
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session, selectinload

from app.investor_memory.service import InvestorMemoryService
from app.models.company import Company
from app.models.knowledge_document import KnowledgeDocument
from app.models.user_followed_stock import UserFollowedStock
from app.recommendation.constants import MAX_CANDIDATES
from app.recommendation.types import RecommendationCandidate

logger = logging.getLogger(__name__)


class RecommendationCandidateBuilder:
    """
    Decoupled candidate builder loading company models, fundamentals, user memory,
    watchlist status, and news articles directly from PostgreSQL (Zero LLM / Zero Vector Embedding API cost).
    """

    @classmethod
    def build_candidates(
        cls,
        db: Session,
        user_id: UUID | None = None,
        retriever_service: Any = None,
        target_sector: str | None = None,
        include_watchlist: bool = True,
        max_candidates: int = MAX_CANDIDATES,
    ) -> tuple[list[RecommendationCandidate], Any]:
        """
        Query DB for active companies, load fundamentals & user memory, fetch recent news per company via direct SQL.
        """
        memory = InvestorMemoryService.get_memory(db, user_id) if user_id else None

        followed_company_ids = set()
        if db and user_id and include_watchlist:
            followed_rows = db.query(UserFollowedStock.company_id).filter(UserFollowedStock.user_id == user_id).all()
            followed_company_ids = {r[0] for r in followed_rows}

        # Query companies with pre-fetched fundamentals
        query = db.query(Company).options(selectinload(Company.fundamentals))

        if target_sector:
            query = query.filter(Company.sector.ilike(f"%{target_sector}%"))

        companies = query.limit(max_candidates).all()

        candidates: list[RecommendationCandidate] = []

        for comp in companies:
            f = getattr(comp, "fundamentals", None)
            fundamentals_dict = {}
            if f:
                fundamentals_dict = {
                    "current_price": float(f.current_price) if f.current_price is not None else None,
                    "market_cap": f.market_cap,
                    "pe_ratio": float(f.pe_ratio) if f.pe_ratio is not None else None,
                    "price_to_book": float(f.price_to_book) if f.price_to_book is not None else None,
                    "eps": float(f.eps) if f.eps is not None else None,
                    "roe": float(f.roe) if f.roe is not None else None,
                    "debt_to_equity": float(f.debt_to_equity) if f.debt_to_equity is not None else None,
                    "dividend_yield": float(f.dividend_yield) if f.dividend_yield is not None else None,
                    "beta": float(f.beta) if f.beta is not None else None,
                    "fifty_two_week_high": float(f.fifty_two_week_high) if f.fifty_two_week_high is not None else None,
                    "fifty_two_week_low": float(f.fifty_two_week_low) if f.fifty_two_week_low is not None else None,
                }

            # Fetch recent news context for candidate via direct PostgreSQL query (Zero Embedding API Call)
            news_items = []
            try:
                docs = (
                    db.query(KnowledgeDocument)
                    .filter(KnowledgeDocument.company_id == comp.id)
                    .order_by(KnowledgeDocument.published_at.desc())
                    .limit(2)
                    .all()
                )
                for d in docs:
                    news_items.append(
                        {
                            "title": d.title,
                            "source_url": d.source_url,
                            "similarity": 1.0,
                            "content": d.summary or (d.content[:200] if d.content else ""),
                        }
                    )
            except Exception as exc:
                logger.warning("Error fetching news docs for candidate %s: %s", comp.ticker, exc)

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

        logger.info("RecommendationCandidateBuilder created %d candidates (Zero LLM/Embedding API Cost)", len(candidates))
        return candidates, memory
