from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.retrieval.service import RetrieverService
from app.schemas.retrieval import RetrievalSearchRequest, RetrievalResponse, RetrievalChunkResponse


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.post("/search", response_model=RetrievalResponse)
def search_retrieval(
    payload: RetrievalSearchRequest,
    db: Session = Depends(get_db),
):
    """
    Perform semantic vector similarity search over pgvector document_embeddings.
    Returns top-K relevant chunks matching query, company filters, and similarity threshold.
    """
    try:
        service = RetrieverService()
        summary = service.retrieve(
            db=db,
            query=payload.query,
            top_k=payload.top_k,
            min_similarity=payload.min_similarity,
            company_id=payload.company_id,
            ticker=payload.ticker,
            published_after=payload.published_after,
        )

        chunk_responses = [
            RetrievalChunkResponse(
                chunk_id=r.chunk_id,
                document_id=r.document_id,
                company_id=r.company_id,
                ticker=r.ticker,
                company_name=r.company_name,
                distance=r.distance,
                similarity=r.similarity,
                content=r.content,
                chunk_index=r.chunk_index,
                source_title=r.source_title,
                source_url=r.source_url,
                published_at=r.published_at,
            )
            for r in summary.results
        ]

        return RetrievalResponse(
            query=summary.query,
            total=summary.total,
            duration_ms=round(summary.duration_seconds * 1000, 2),
            chunks=chunk_responses,
        )

    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        ) from val_err
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic retrieval search failed: {exc}",
        ) from exc
