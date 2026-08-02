from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.knowledge_document import KnowledgeDocument
from app.services.company_service import CompanyService
from app.ingestion.news.pipeline import NewsPipeline

router = APIRouter(prefix="/api/news", tags=["News"])


class IngestTickerRequest(BaseModel):
    ticker: str


@router.get("/latest")
def get_latest_news(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Retrieve latest ingested news articles directly from PostgreSQL (Zero LLMs / Zero Vector Searches)."""
    docs = (
        db.query(KnowledgeDocument)
        .order_by(KnowledgeDocument.published_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": str(d.id),
            "title": d.title,
            "summary": d.summary or (d.content[:200] + "..." if d.content else "No summary available."),
            "source": d.source,
            "source_url": d.source_url,
            "published_at": d.published_at.isoformat() if d.published_at else None,
            "sentiment": "Positive" if "growth" in d.title.lower() or "profit" in d.title.lower() or "rally" in d.title.lower() else "Bullish" if "deal" in d.title.lower() else "Neutral",
        }
        for d in docs
    ]


@router.post("/ingest")
def ingest_ticker_news(
    payload: IngestTickerRequest,
    db: Session = Depends(get_db),
):
    """Ingest live RSS news & SEC filings for a company ticker into PostgreSQL & pgvector."""
    ticker_clean = payload.ticker.strip().upper()
    if not ticker_clean:
        raise HTTPException(status_code=400, detail="Ticker symbol cannot be empty.")

    company = CompanyService.get_company_by_ticker(db, ticker_clean)
    if not company:
        # Auto-create company record if not yet existing
        from app.schemas.company import CompanyBase
        company = CompanyService.create_company(
            db,
            CompanyBase(
                ticker=ticker_clean,
                company_name=f"{ticker_clean} Ltd",
                exchange="NSE",
                sector="General Market",
                is_active=True,
            ),
        )

    res = NewsPipeline.ingest_company(db, company)

    return {
        "success": True,
        "ticker": company.ticker,
        "company_name": company.company_name,
        "processed": res.processed,
        "created": res.created,
        "updated": res.updated,
        "duplicates": res.duplicates,
        "message": f"Successfully ingested {res.created} new articles for {company.ticker} into PostgreSQL & pgvector!",
    }
