import logging
from datetime import datetime, timezone
from app.investor_memory.types import MemoryExtraction, MemoryUpdate
from app.investor_memory.utils import merge_lists, calculate_confidence
from app.models.investor_memory import InvestorMemory

logger = logging.getLogger(__name__)


class MemoryMergeEngine:
    """
    Isolated merge engine combining candidate MemoryUpdate extractions into an existing InvestorMemory model.
    """

    @classmethod
    def merge(cls, existing: InvestorMemory, update: MemoryUpdate) -> InvestorMemory:
        """
        Merge candidate extraction fields into existing memory model with conflict resolution rules.
        """
        ext: MemoryExtraction = update.extraction

        # Update scalar fields if present in extraction
        if ext.risk_profile:
            existing.risk_profile = ext.risk_profile

        if ext.investment_horizon:
            existing.investment_horizon = ext.investment_horizon

        if ext.preferred_market_cap:
            existing.preferred_market_cap = ext.preferred_market_cap

        if ext.investment_style:
            existing.investment_style = ext.investment_style

        if ext.dividend_preference:
            existing.dividend_preference = ext.dividend_preference

        if ext.esg_preference is not None:
            existing.esg_preference = ext.esg_preference

        if ext.preferred_hold_period:
            existing.preferred_hold_period = ext.preferred_hold_period

        if ext.memory_summary:
            existing.memory_summary = ext.memory_summary

        # Merge JSONB array lists
        existing.preferred_sectors = merge_lists(existing.preferred_sectors, ext.preferred_sectors)
        existing.avoided_sectors = merge_lists(existing.avoided_sectors, ext.avoided_sectors)
        existing.preferred_industries = merge_lists(existing.preferred_industries, ext.preferred_industries)
        existing.preferred_assets = merge_lists(existing.preferred_assets, ext.preferred_assets)
        existing.memory_facts = merge_lists(existing.memory_facts, ext.memory_facts)
        existing.notes = merge_lists(existing.notes, ext.notes)

        # Provenance metadata
        existing.memory_source = ext.memory_source
        if update.source_message_id:
            existing.source_message_id = update.source_message_id
        if update.source_conversation_id:
            existing.source_conversation_id = update.source_conversation_id

        # Recalculate empirical confidence
        facts_count = len(existing.memory_facts or [])
        existing.confidence_score = calculate_confidence(
            facts_count=facts_count,
            has_risk=existing.risk_profile is not None,
            has_horizon=existing.investment_horizon is not None,
        )

        existing.last_updated_from_chat = datetime.now(timezone.utc)
        return existing
