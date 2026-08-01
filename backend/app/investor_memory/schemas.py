from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field


class InvestorMemoryRequest(BaseModel):
    """Input schema for manually creating or updating investor memory profile."""
    risk_profile: str | None = Field(default=None, description="Conservative | Moderate | Aggressive")
    investment_horizon: str | None = Field(default=None, description="Short Term | Medium Term | Long Term")
    preferred_sectors: list[str] | None = Field(default=None, description="List of preferred stock sectors")
    avoided_sectors: list[str] | None = Field(default=None, description="List of avoided sectors")
    preferred_market_cap: str | None = Field(default=None, description="Large Cap | Mid Cap | Small Cap")
    preferred_industries: list[str] | None = Field(default=None, description="Preferred industry niches")
    preferred_assets: list[str] | None = Field(default=None, description="Stocks, ETFs, Mutual Funds, Bonds")
    investment_style: str | None = Field(default=None, description="Growth | Value | Dividend | Index")
    dividend_preference: str | None = Field(default=None, description="High | Low")
    esg_preference: bool | None = Field(default=None, description="ESG compliance preference")
    preferred_hold_period: str | None = Field(default=None, description="Holding timeframe")
    memory_summary: str | None = Field(default=None, description="Summary description")
    memory_facts: list[str] | None = Field(default=None, description="Observed facts list")
    notes: list[str] | None = Field(default=None, description="Additional notes")


class InvestorMemoryResponse(BaseModel):
    """Output response schema for investor memory profile."""
    id: UUID
    user_id: UUID
    risk_profile: str | None
    investment_horizon: str | None
    preferred_sectors: list[str] = Field(default_factory=list)
    avoided_sectors: list[str] = Field(default_factory=list)
    preferred_market_cap: str | None
    preferred_industries: list[str] = Field(default_factory=list)
    preferred_assets: list[str] = Field(default_factory=list)
    investment_style: str | None
    dividend_preference: str | None
    esg_preference: bool | None
    preferred_hold_period: str | None
    memory_summary: str | None
    memory_facts: list[str] = Field(default_factory=list)
    memory_source: str
    confidence_score: float
    memory_version: str
    last_confirmed_at: datetime | None
    last_updated_from_chat: datetime | None
    notes: list[str] = Field(default_factory=list)


class MemoryContextResponse(BaseModel):
    """Schema returning rendered Markdown prompt context string."""
    prompt_context: str
    has_profile: bool
    confidence: float
    last_updated: datetime | None


class MemoryStatsResponse(BaseModel):
    """Schema returning high level memory statistics."""
    user_id: UUID
    has_profile: bool
    facts_count: int
    confidence: float
    version: str
    last_updated: datetime | None
