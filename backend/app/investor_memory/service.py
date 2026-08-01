import logging
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session

from app.investor_memory.constants import MIN_CONFIDENCE
from app.investor_memory.extractor import MemoryExtractor
from app.investor_memory.merge import MemoryMergeEngine
from app.investor_memory.types import MemoryExtraction, MemorySummary, MemoryUpdate
from app.models.investor_memory import InvestorMemory

logger = logging.getLogger(__name__)


class InvestorMemoryService:
    """
    Service managing investor memory database CRUD, conflict resolution merging, and background extraction.
    """

    @classmethod
    def get_memory(cls, db: Session, user_id: UUID) -> InvestorMemory | None:
        """Fetch investor memory profile for a given user UUID."""
        return db.query(InvestorMemory).filter(InvestorMemory.user_id == user_id).first()

    @classmethod
    def get_or_create_memory(cls, db: Session, user_id: UUID) -> InvestorMemory:
        """Get existing investor memory or create new blank model for user."""
        memory = cls.get_memory(db, user_id)
        if not memory:
            memory = InvestorMemory(
                user_id=user_id,
                preferred_sectors=[],
                avoided_sectors=[],
                preferred_industries=[],
                preferred_assets=[],
                memory_facts=[],
                notes=[],
                confidence_score=0.50,
            )
            db.add(memory)
            db.commit()
            db.refresh(memory)
            logger.info("Created new InvestorMemory record for user %s", user_id)
        return memory

    @classmethod
    def update_memory(
        cls,
        db: Session,
        user_id: UUID,
        update_data: dict,
    ) -> InvestorMemory:
        """Manually update investor memory profile from API request."""
        memory = cls.get_or_create_memory(db, user_id)

        for key, val in update_data.items():
            if hasattr(memory, key) and val is not None:
                setattr(memory, key, val)

        memory.memory_source = "manual_api"
        memory.last_confirmed_at = datetime.now(timezone.utc)
        memory.confidence_score = 1.0

        db.commit()
        db.refresh(memory)
        return memory

    @classmethod
    def delete_memory(cls, db: Session, user_id: UUID) -> bool:
        """Delete investor memory profile for user."""
        memory = cls.get_memory(db, user_id)
        if memory:
            db.delete(memory)
            db.commit()
            logger.info("Deleted InvestorMemory profile for user %s", user_id)
            return True
        return False

    @classmethod
    def save_from_extraction(
        cls,
        db: Session,
        user_id: UUID,
        extraction: MemoryExtraction,
        source_message_id: UUID | None = None,
        source_conversation_id: UUID | None = None,
    ) -> InvestorMemory | None:
        """
        Merge extracted preferences into database only if extraction confidence exceeds threshold.
        """
        if extraction.confidence < MIN_CONFIDENCE:
            logger.info("Skipping memory merge: extraction confidence %.2f below threshold %.2f", extraction.confidence, MIN_CONFIDENCE)
            return None

        memory = cls.get_or_create_memory(db, user_id)
        update = MemoryUpdate(
            extraction=extraction,
            user_id=user_id,
            source_message_id=source_message_id,
            source_conversation_id=source_conversation_id,
        )

        memory = MemoryMergeEngine.merge(memory, update)
        db.commit()
        db.refresh(memory)
        logger.info("Successfully merged InvestorMemory for user %s (confidence: %.2f)", user_id, memory.confidence_score)
        return memory

    @classmethod
    def refresh_memory_from_history(
        cls,
        db: Session,
        user_id: UUID,
        chat_history: str,
        extractor: MemoryExtractor | None = None,
    ) -> InvestorMemory | None:
        """Rebuild/merge memory profile by extracting preferences from full chat history."""
        active_extractor = extractor or MemoryExtractor()
        extraction = active_extractor.extract(chat_history)
        return cls.save_from_extraction(db, user_id, extraction)

    @classmethod
    def get_summary(cls, db: Session, user_id: UUID) -> MemorySummary:
        """Return structured summary statistics for investor memory profile."""
        memory = cls.get_memory(db, user_id)
        if not memory:
            return MemorySummary(
                user_id=user_id,
                has_profile=False,
                risk_profile=None,
                investment_horizon=None,
                preferred_sectors=[],
                avoided_sectors=[],
                facts_count=0,
                confidence_score=0.0,
                memory_version="v1",
                last_updated=None,
            )

        return MemorySummary(
            user_id=user_id,
            has_profile=True,
            risk_profile=memory.risk_profile,
            investment_horizon=memory.investment_horizon,
            preferred_sectors=memory.preferred_sectors or [],
            avoided_sectors=memory.avoided_sectors or [],
            facts_count=len(memory.memory_facts or []),
            confidence_score=memory.confidence_score,
            memory_version=memory.memory_version,
            last_updated=memory.last_updated_from_chat or memory.updated_at,
        )
