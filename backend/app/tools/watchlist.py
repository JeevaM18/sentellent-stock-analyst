import time
import logging
from typing import Any
from sqlalchemy.orm import Session, joinedload

from app.models.user_followed_stock import UserFollowedStock
from app.retrieval.service import RetrieverService
from app.tools.base import BaseAgentTool

logger = logging.getLogger(__name__)


class WatchlistIntelligenceTool(BaseAgentTool):
    """
    Watchlist Intelligence Tool querying user's followed stocks and aggregating
    recent news articles and vector context per portfolio stock.
    """

    name = "watchlist"
    description = "Fetches user's followed watchlist stocks and retrieves recent company news and vector context."

    def run(
        self,
        db: Session | None = None,
        user_id: Any = None,
        retriever: RetrieverService | None = None,
        query: str = "",
        top_k_per_stock: int = 2,
        **kwargs: Any,
    ) -> dict[str, Any]:
        start_time = time.perf_counter()

        followed_companies = []
        if db and user_id:
            followed_rows = (
                db.query(UserFollowedStock)
                .options(joinedload(UserFollowedStock.company))
                .filter(UserFollowedStock.user_id == user_id)
                .all()
            )
            followed_companies = [r.company for r in followed_rows if getattr(r, "company", None)]

        if not followed_companies:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            formatted_context = "Your watchlist currently contains no followed stocks."
            return self.format_output(
                tool_name=self.name,
                status="empty",
                execution_ms=duration_ms,
                formatted_context=formatted_context,
                data={"count": 0, "companies": []},
            )

        active_retriever = retriever or RetrieverService()
        companies_data = []
        all_citations = []
        formatted_lines = [
            f"=== Watchlist Portfolio News & Intelligence ({len(followed_companies)} stocks) ===",
        ]

        for company in followed_companies:
            name = str(getattr(company, "company_name", ""))
            ticker = str(getattr(company, "ticker", ""))
            sector = str(getattr(company, "sector", "N/A"))

            # Retrieve news context for specific company ticker/name
            search_query = f"{name} {ticker} news earnings performance"
            company_news = []

            if db:
                try:
                    summary = active_retriever.retrieve(db=db, query=search_query, top_k=top_k_per_stock)
                    for idx, chunk in enumerate(summary.results, 1):
                        all_citations.append(
                            {
                                "rank": len(all_citations) + 1,
                                "title": chunk.chunk.document.title if chunk.chunk and chunk.chunk.document else name,
                                "source_url": chunk.chunk.document.source_url if chunk.chunk and chunk.chunk.document else None,
                                "ticker": ticker,
                                "similarity": round(chunk.similarity, 4),
                            }
                        )
                        company_news.append(
                            {
                                "title": chunk.chunk.document.title if chunk.chunk and chunk.chunk.document else f"{name} Update",
                                "snippet": chunk.chunk.content[:200] if chunk.chunk else "",
                                "similarity": round(chunk.similarity, 4),
                            }
                        )
                except Exception as exc:
                    logger.warning("Watchlist intelligence news fetch error for ticker %s: %s", ticker, exc)

            companies_data.append(
                {
                    "ticker": ticker,
                    "name": name,
                    "sector": sector,
                    "news_count": len(company_news),
                    "news": company_news,
                }
            )

            formatted_lines.append(f"\n• {name} ({ticker}) [{sector or 'N/A'}]")
            if company_news:
                for n in company_news:
                    formatted_lines.append(f"  - News: {n['title']} (Relevance: {n['similarity']})")
            else:
                formatted_lines.append("  - News: No recent articles retrieved in knowledge base.")

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        formatted_context = "\n".join(formatted_lines)

        return self.format_output(
            tool_name=self.name,
            status="success",
            execution_ms=duration_ms,
            formatted_context=formatted_context,
            data={"count": len(followed_companies), "companies": companies_data},
            citations=all_citations,
        )
