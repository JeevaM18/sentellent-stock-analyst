import logging
import time
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session, joinedload

from app.embeddings.google_provider import GoogleEmbeddingProvider
from app.embeddings.provider import BaseEmbeddingProvider
from app.models.company import Company
from app.models.document_chunk import DocumentChunk
from app.models.document_embedding import DocumentEmbedding
from app.models.knowledge_document import KnowledgeDocument
from app.retrieval.constants import CANDIDATE_MULTIPLIER, DEFAULT_MIN_SIMILARITY, DEFAULT_TOP_K, MAX_TOP_K
from app.retrieval.types import RetrievalResult, RetrievalSummary
from app.retrieval.utils import clamp_top_k, cosine_distance_to_similarity, validate_query

logger = logging.getLogger(__name__)


class RetrieverService:
    """Service performing pgvector semantic vector search with relationship preloading and filters."""

    def __init__(self, provider: BaseEmbeddingProvider | None = None):
        self.provider = provider or GoogleEmbeddingProvider()

    def retrieve(
        self,
        *,
        db: Session,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        min_similarity: float = DEFAULT_MIN_SIMILARITY,
        company_id: UUID | None = None,
        ticker: str | None = None,
        published_after: datetime | None = None,
    ) -> RetrievalSummary:
        """Perform semantic search using pgvector cosine distance and return RetrievalSummary."""
        start_time = time.perf_counter()
        clean_query = validate_query(query)
        effective_top_k = clamp_top_k(top_k)

        # Generate query vector embedding
        query_result = self.provider.embed_text(text=clean_query)
        query_vector = query_result.vector

        # Base pgvector cosine distance query with eager loading of ORM relationships
        distance_expr = DocumentEmbedding.embedding.cosine_distance(query_vector).label("distance")
        q = (
            db.query(DocumentEmbedding, distance_expr)
            .join(DocumentEmbedding.chunk)
            .join(DocumentChunk.document)
            .outerjoin(KnowledgeDocument.company)
            .options(
                joinedload(DocumentEmbedding.chunk)
                .joinedload(DocumentChunk.document)
                .joinedload(KnowledgeDocument.company)
            )
        )

        # Apply optional filters
        if company_id:
            q = q.filter(KnowledgeDocument.company_id == company_id)
        if ticker:
            q = q.filter(Company.ticker == ticker.strip().upper())
        if published_after:
            q = q.filter(KnowledgeDocument.published_at >= published_after)

        # Retrieve top_k * CANDIDATE_MULTIPLIER candidates before threshold filtering
        candidate_limit = min(effective_top_k * CANDIDATE_MULTIPLIER, MAX_TOP_K * 2)
        rows = q.order_by(distance_expr.asc()).limit(candidate_limit).all()

        results: list[RetrievalResult] = []
        for emb, dist in rows:
            dist_val = float(dist)
            sim_val = cosine_distance_to_similarity(dist_val)

            if sim_val < min_similarity:
                logger.debug("Skipping result with similarity %.4f < threshold %.4f", sim_val, min_similarity)
                continue

            chunk: DocumentChunk = emb.chunk
            doc: KnowledgeDocument = chunk.document
            company: Company | None = doc.company

            results.append(
                RetrievalResult(
                    chunk_id=chunk.id,
                    document_id=doc.id,
                    company_id=doc.company_id,
                    ticker=company.ticker if company else None,
                    company_name=company.company_name if company else None,
                    distance=round(dist_val, 4),
                    similarity=sim_val,
                    content=chunk.content,
                    chunk_index=chunk.chunk_index,
                    source_title=doc.title,
                    source_url=doc.source_url,
                    published_at=doc.published_at,
                )
            )

            if len(results) >= effective_top_k:
                break

        duration_seconds = round(time.perf_counter() - start_time, 4)
        logger.info(
            "Retrieved %d results for query '%s' in %.2f ms",
            len(results),
            clean_query,
            duration_seconds * 1000,
        )

        return RetrievalSummary(
            query=clean_query,
            total=len(results),
            duration_seconds=duration_seconds,
            results=results,
        )
