from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from app.models.company import Company
from app.models.investor_memory import InvestorMemory


@dataclass(slots=True)
class RecommendationCandidate:
    """Dataclass encapsulating candidate stock company data, fundamentals, memory context, and news."""
    company: Company
    ticker: str
    company_id: UUID
    fundamentals: dict[str, Any] = field(default_factory=dict)
    retrieved_news: list[dict[str, Any]] = field(default_factory=list)
    in_watchlist: bool = False
    memory: InvestorMemory | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RecommendationScore:
    """Dataclass storing individual sub-scores and combined weighted score."""
    fundamental_score: float = 0.0
    news_score: float = 0.0
    memory_score: float = 0.0
    portfolio_score: float = 0.0
    trend_score: float = 0.0
    overall_score: float = 0.0
    confidence: float = 0.75


@dataclass(slots=True)
class RecommendationReason:
    """Dataclass describing specific reason supporting stock recommendation."""
    title: str
    description: str
    importance: float = 1.0  # Weight/importance
    category: str = "fundamentals"  # "fundamentals" | "news" | "memory" | "portfolio" | "trend"


@dataclass(slots=True)
class RecommendationEvidence:
    """Dataclass containing supporting evidence data separate from LLM explanations."""
    news_titles: list[str] = field(default_factory=list)
    fundamental_metrics: dict[str, Any] = field(default_factory=dict)
    memory_matches: list[str] = field(default_factory=list)
    portfolio_analysis: str = ""
    citations: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class RecommendationResult:
    """Dataclass representing a complete scored recommendation item for a single stock."""
    company_name: str
    ticker: str
    exchange: str
    score: RecommendationScore
    reasons: list[RecommendationReason] = field(default_factory=list)
    evidence: RecommendationEvidence = field(default_factory=RecommendationEvidence)
    summary: str = ""
    risk_level: str = "Moderate"
    expected_horizon: str = "Long Term"


@dataclass(slots=True)
class RecommendationSummary:
    """Dataclass summarizing recommendations execution stats and metadata."""
    total_candidates: int
    evaluated_count: int
    top_k: int
    version: str = "v1"
    execution_time_ms: float = 0.0
