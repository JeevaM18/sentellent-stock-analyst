import logging
from app.investor_memory.types import MemoryContext
from app.models.investor_memory import InvestorMemory

logger = logging.getLogger(__name__)


class MemoryBuilder:
    """
    Constructs clean Markdown system prompt strings from InvestorMemory database models
    to inject personalized investor context into LLM generation prompts.
    """

    @classmethod
    def build(cls, memory: InvestorMemory | None) -> MemoryContext:
        """Build formatted Markdown prompt context string from InvestorMemory model."""
        if not memory:
            return MemoryContext(
                prompt_context="",
                has_profile=False,
                confidence=0.0,
                last_updated=None,
            )

        lines = ["=== Personalized Investor Profile Memory ==="]

        if memory.risk_profile:
            lines.append(f"• Risk Profile: {memory.risk_profile}")

        if memory.investment_horizon:
            lines.append(f"• Investment Horizon: {memory.investment_horizon}")

        if memory.investment_style:
            lines.append(f"• Investment Style: {memory.investment_style}")

        if memory.preferred_market_cap:
            lines.append(f"• Market Cap Preference: {memory.preferred_market_cap}")

        if memory.preferred_sectors:
            lines.append(f"• Preferred Sectors: {', '.join(memory.preferred_sectors)}")

        if memory.avoided_sectors:
            lines.append(f"• Avoided Sectors: {', '.join(memory.avoided_sectors)}")

        if memory.preferred_assets:
            lines.append(f"• Preferred Assets: {', '.join(memory.preferred_assets)}")

        if memory.dividend_preference:
            lines.append(f"• Dividend Preference: {memory.dividend_preference}")

        if memory.memory_summary:
            lines.append(f"\nExecutive Summary:\n  {memory.memory_summary}")

        if memory.memory_facts:
            lines.append("\nObserved Investor Facts:")
            for fact in memory.memory_facts[:10]:
                lines.append(f"  - {fact}")

        prompt_str = "\n".join(lines)
        return MemoryContext(
            prompt_context=prompt_str,
            has_profile=True,
            confidence=memory.confidence_score,
            last_updated=memory.last_updated_from_chat or memory.updated_at,
        )
