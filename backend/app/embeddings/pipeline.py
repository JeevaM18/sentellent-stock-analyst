import logging
import time
from typing import Any
from sqlalchemy.orm import Session

from app.constants.chunks import CHUNK_STATUS_EMBEDDED, CHUNK_STATUS_FAILED
from app.embeddings.constants import EMBEDDING_BATCH_SIZE
from app.embeddings.exceptions import EmbeddingProviderError
from app.embeddings.google_provider import GoogleEmbeddingProvider
from app.embeddings.provider import BaseEmbeddingProvider
from app.embeddings.types import EmbeddingJob, EmbeddingPipelineSummary
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class EmbeddingPipeline:
    """Orchestration pipeline fetching pending chunks, generating vectors, and persisting to pgvector."""

    def __init__(self, provider: BaseEmbeddingProvider | None = None):
        self.provider = provider or GoogleEmbeddingProvider()

    def embed_chunk(
        self, *, db: Session, chunk: DocumentChunk
    ) -> EmbeddingPipelineSummary:
        """Embed a single DocumentChunk instance."""
        summary = EmbeddingPipelineSummary()

        if chunk.status == CHUNK_STATUS_EMBEDDED:
            logger.info("Chunk %s already embedded. Skipping.", chunk.id)
            return summary

        summary.processed = 1
        try:
            res = self.provider.embed_text(
                text=chunk.content,
                metadata={"chunk_index": chunk.chunk_index, "document_id": str(chunk.document_id)},
            )
            record, created = EmbeddingService.ingest(
                db, chunk_id=chunk.id, embedding_result=res
            )
            if created:
                summary.created = 1
            else:
                summary.updated = 1
            logger.info("Successfully embedded chunk %s (created=%s)", chunk.id, created)

        except (EmbeddingProviderError, Exception) as exc:
            logger.error("Failed to embed chunk %s: %s", chunk.id, exc)
            summary.failed = 1
            chunk.status = CHUNK_STATUS_FAILED
            db.commit()

        return summary

    def embed_chunks(
        self, *, db: Session, chunks: list[DocumentChunk]
    ) -> EmbeddingPipelineSummary:
        """Embed a list of DocumentChunks using batch provider API and single-transaction bulk DB persistence."""
        summary = EmbeddingPipelineSummary()
        if not chunks:
            return summary

        # Defensive filtering: skip already embedded chunks
        valid_chunks: list[DocumentChunk] = []
        for c in chunks:
            if c.status == CHUNK_STATUS_EMBEDDED:
                logger.info("Chunk %s is already embedded. Skipping.", c.id)
            else:
                valid_chunks.append(c)

        if not valid_chunks:
            return summary

        summary.processed = len(valid_chunks)
        texts = [c.content for c in valid_chunks]
        metadatas = [{"chunk_index": c.chunk_index, "document_id": str(c.document_id)} for c in valid_chunks]

        try:
            logger.info("Generating embeddings for batch of %d chunks...", len(valid_chunks))
            results = self.provider.embed_batch(texts=texts, metadatas=metadatas)

            jobs: list[EmbeddingJob] = []
            for index, (chunk, res) in enumerate(zip(valid_chunks, results)):
                logger.info("Embedding chunk %s (%d/%d)", chunk.id, index + 1, len(valid_chunks))
                jobs.append(EmbeddingJob(chunk_id=chunk.id, embedding=res))

            ingest_stats = EmbeddingService.bulk_ingest(db, jobs)
            summary.created = ingest_stats.get("created", 0)
            summary.updated = ingest_stats.get("updated", 0)
            summary.failed = ingest_stats.get("failed", 0)

            logger.info("Batch embedding completed: created=%d, updated=%d, failed=%d", summary.created, summary.updated, summary.failed)

        except (EmbeddingProviderError, Exception) as exc:
            logger.error("Batch embedding generation failed: %s", exc)
            summary.failed = len(valid_chunks)
            for c in valid_chunks:
                c.status = CHUNK_STATUS_FAILED
            db.commit()

        return summary

    def embed_pending(
        self, *, db: Session, limit: int = EMBEDDING_BATCH_SIZE
    ) -> EmbeddingPipelineSummary:
        """Fetch pending DocumentChunks awaiting vector generation and embed in batch."""
        start_time = time.perf_counter()

        pending_chunks = EmbeddingService.get_pending_chunks(db, limit=limit)
        if not pending_chunks:
            logger.info("No pending chunks requiring vector embedding.")
            return EmbeddingPipelineSummary(duration_seconds=round(time.perf_counter() - start_time, 2))

        logger.info("Found %d pending chunks requiring vector embedding.", len(pending_chunks))
        summary = self.embed_chunks(db=db, chunks=pending_chunks)
        summary.duration_seconds = round(time.perf_counter() - start_time, 2)

        logger.info("Embedding pipeline completed: %s", summary)
        return summary
