import logging
from app.investor_memory.builder import MemoryBuilder
from app.models.investor_memory import InvestorMemory
from app.recommendation.types import RecommendationResult

logger = logging.getLogger(__name__)


class RecommendationContextBuilder:
    """
    Renders structured Markdown context of ranked recommendations and scoring details
    to supply strictly grounded evidence for Gemini LLM explanation generation.
    """

    @classmethod
    def build_context(
        cls,
        results: list[RecommendationResult],
        memory: InvestorMemory | None = None,
    ) -> str:
        """Build comprehensive sectioned Markdown context string."""
        lines = ["=== Deterministic Recommendation Engine Analysis & Evidence ==="]

        # Section 1: Investor Profile Context
        if memory:
            mem_ctx = MemoryBuilder.build(memory)
            if mem_ctx.has_profile:
                lines.append(f"\n{mem_ctx.prompt_context}")

        # Section 2: Scored & Ranked Stock Recommendations
        lines.append(f"\nTop {len(results)} Scored Recommendations:")

        for idx, r in enumerate(results, 1):
            s = r.score
            lines.append(f"\n[{idx}] {r.company_name} ({r.ticker}) — Overall Score: {s.overall_score:.1f}/100 (Confidence: {s.confidence:.2f})")
            lines.append(f"  Score Breakdown:")
            lines.append(f"    - Fundamentals (35%): {s.fundamental_score:.1f}")
            lines.append(f"    - News Relevance (25%): {s.news_score:.1f}")
            lines.append(f"    - Investor Memory Match (20%): {s.memory_score:.1f}")
            lines.append(f"    - Portfolio Impact (10%): {s.portfolio_score:.1f}")
            lines.append(f"    - Trend Momentum (10%): {s.trend_score:.1f}")

            if r.reasons:
                lines.append("  Key Supporting Reasons:")
                for reason in r.reasons[:4]:
                    lines.append(f"    • [{reason.category.upper()}] {reason.title}: {reason.description}")

            f = r.evidence.fundamental_metrics
            if f:
                lines.append("  Key Financial Metrics:")
                lines.append(f"    - Current Price: ₹{f.get('current_price')}" if f.get('current_price') else "    - Price: N/A")
                lines.append(f"    - P/E Ratio: {f.get('pe_ratio')}" if f.get('pe_ratio') else "    - P/E: N/A")
                lines.append(f"    - ROE: {f.get('roe')}%" if f.get('roe') else "    - ROE: N/A")
                lines.append(f"    - Debt/Equity: {f.get('debt_to_equity')}" if f.get('debt_to_equity') else "    - D/E: N/A")

            if r.evidence.news_titles:
                lines.append("  Recent News Coverage:")
                for news_title in r.evidence.news_titles[:2]:
                    lines.append(f"    - News: {news_title}")

        return "\n".join(lines)
