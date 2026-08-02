from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.constants import SUPPORTED_EXCHANGES, SUPPORTED_SECTORS
from app.models.knowledge_document import KnowledgeDocument
from app.schemas.company import CompanyResponse, PaginatedCompanyResponse
from app.services.company_service import CompanyService

router = APIRouter(
    prefix="/api/companies",
    tags=["Companies"],
)


@router.get(
    "",
    response_model=PaginatedCompanyResponse,
)
def list_companies(
    search: str | None = Query(None, description="Search by ticker, name, or symbol"),
    sector: str | None = Query(None, description="Filter by sector"),
    exchange: str | None = Query(None, description="Filter by exchange (e.g. NSE)"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Search and filter listed companies with pagination."""
    companies, total = CompanyService.search_companies(
        db=db,
        search=search,
        sector=sector,
        exchange=exchange,
        is_active=is_active,
        page=page,
        limit=limit,
    )
    return PaginatedCompanyResponse(
        total=total,
        page=page,
        limit=limit,
        companies=companies,
    )


@router.get(
    "/sectors",
    response_model=list[str],
)
def get_supported_sectors():
    """Retrieve list of supported sectors for dropdown filters."""
    return SUPPORTED_SECTORS


@router.get(
    "/exchanges",
    response_model=list[str],
)
def get_supported_exchanges():
    """Retrieve list of supported exchanges for dropdown filters."""
    return SUPPORTED_EXCHANGES


@router.get(
    "/ticker/{ticker}",
    response_model=CompanyResponse,
)
def get_company_by_ticker(
    ticker: str,
    db: Session = Depends(get_db),
):
    """Retrieve company details by ticker symbol (e.g., RELIANCE)."""
    company = CompanyService.get_company_by_ticker(db, ticker)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker '{ticker.upper()}' not found",
        )
    return company


@router.get("/ticker/{ticker}/news")
def get_company_news_by_ticker(
    ticker: str,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Retrieve company news directly from PostgreSQL without vector search or LLMs."""
    company = CompanyService.get_company_by_ticker(db, ticker)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker '{ticker.upper()}' not found",
        )

    docs = (
        db.query(KnowledgeDocument)
        .filter(KnowledgeDocument.company_id == company.id)
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
            "sentiment": "Positive" if "growth" in d.title.lower() or "profit" in d.title.lower() else "Neutral",
        }
        for d in docs
    ]


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
def get_company_by_id(
    company_id: UUID,
    db: Session = Depends(get_db),
):
    """Retrieve company details by unique UUID."""
    company = CompanyService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found",
        )
    return company


# Development only
@router.post(
    "/seed",
    status_code=status.HTTP_200_OK,
)
def dev_seed_companies(
    db: Session = Depends(get_db),
):
    """# Development only endpoint to trigger company master seeding."""
    from app.scripts.seed_companies import run_seeder
    inserted, skipped = run_seeder(db)
    return {
        "message": "Company master seeding completed",
        "inserted": inserted,
        "skipped": skipped,
    }
