from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(slots=True)
class InvestorPreference:
    """Dataclass encapsulating structured investor preference fields."""
    risk_profile: str | None = None
    investment_horizon: str | None = None
    preferred_sectors: list[str] = field(default_factory=list)
    avoided_sectors: list[str] = field(default_factory=list)
    preferred_market_cap: str | None = None
    preferred_industries: list[str] = field(default_factory=list)
    preferred_assets: list[str] = field(default_factory=list)
    investment_style: str | None = None
    dividend_preference: str | None = None
    esg_preference: bool | None = None
    preferred_hold_period: str | None = None


@dataclass(slots=True)
class MemoryExtraction:
    """Dataclass encapsulating extracted preferences from LLM analysis."""
    risk_profile: str | None = None
    investment_horizon: str | None = None
    preferred_sectors: list[str] = field(default_factory=list)
    avoided_sectors: list[str] = field(default_factory=list)
    preferred_market_cap: str | None = None
    preferred_industries: list[str] = field(default_factory=list)
    preferred_assets: list[str] = field(default_factory=list)
    investment_style: str | None = None
    dividend_preference: str | None = None
    esg_preference: bool | None = None
    preferred_hold_period: str | None = None
    memory_summary: str | None = None
    memory_facts: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    confidence: float = 0.85
    memory_source: str = "conversation"


@dataclass(slots=True)
class MemoryContext:
    """Dataclass representing formatted prompt string context and metadata."""
    prompt_context: str
    has_profile: bool
    confidence: float = 1.0
    last_updated: datetime | None = None


@dataclass(slots=True)
class MemoryUpdate:
    """Dataclass wrapping a candidate update to merge into InvestorMemory."""
    extraction: MemoryExtraction
    source_message_id: UUID | None = None
    source_conversation_id: UUID | None = None
    user_id: UUID | None = None


@dataclass(slots=True)
class MemorySummary:
    """Dataclass summarizing memory statistics for API responses."""
    user_id: UUID
    has_profile: bool
    risk_profile: str | None
    investment_horizon: str | None
    preferred_sectors: list[str]
    avoided_sectors: list[str]
    facts_count: int
    confidence_score: float
    memory_version: str
    last_updated: datetime | None
