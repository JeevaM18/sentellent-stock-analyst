import json
import logging
import re
from typing import Any

from app.investor_memory.prompts import (
    MEMORY_EXTRACTION_SYSTEM_PROMPT,
    MEMORY_EXTRACTION_USER_PROMPT,
)
from app.investor_memory.types import MemoryExtraction
from app.llm.service import GenerationService

logger = logging.getLogger(__name__)


class MemoryExtractor:
    """
    Extracts structured investor preferences and memory facts from chat history using LLM generation.
    """

    def __init__(self, generation_service: GenerationService | None = None) -> None:
        self.gen_service = generation_service or GenerationService()

    def extract(self, chat_history: str) -> MemoryExtraction:
        """Analyze chat history and return extracted MemoryExtraction dataclass."""
        if not chat_history or len(chat_history.strip()) < 10:
            return MemoryExtraction(confidence=0.0)

        prompt = MEMORY_EXTRACTION_USER_PROMPT.format(chat_history=chat_history)

        try:
            raw_text = self.gen_service.generate_raw(
                system_prompt=MEMORY_EXTRACTION_SYSTEM_PROMPT,
                user_prompt=prompt,
            )
            return self.parse_json(raw_text)
        except Exception as exc:
            logger.warning("MemoryExtractor LLM extraction failed: %s", exc)
            return self._heuristic_extract(chat_history)

    def parse_json(self, raw_text: str) -> MemoryExtraction:
        """Parse structured JSON from raw text response."""
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if not json_match:
            raise ValueError("No valid JSON found in LLM extraction response")

        data = json.loads(json_match.group(0))

        return MemoryExtraction(
            risk_profile=data.get("risk_profile"),
            investment_horizon=data.get("investment_horizon"),
            preferred_sectors=data.get("preferred_sectors") or [],
            avoided_sectors=data.get("avoided_sectors") or [],
            preferred_market_cap=data.get("preferred_market_cap"),
            preferred_industries=data.get("preferred_industries") or [],
            preferred_assets=data.get("preferred_assets") or [],
            investment_style=data.get("investment_style"),
            dividend_preference=data.get("dividend_preference"),
            esg_preference=data.get("esg_preference"),
            preferred_hold_period=data.get("preferred_hold_period"),
            memory_summary=data.get("memory_summary"),
            memory_facts=data.get("memory_facts") or [],
            confidence=float(data.get("confidence", 0.85)),
        )

    def _heuristic_extract(self, text: str) -> MemoryExtraction:
        """Fallback regex extraction when LLM extraction is unavailable."""
        t = text.lower()
        extracted = MemoryExtraction(confidence=0.60)

        if "conservative" in t:
            extracted.risk_profile = "Conservative"
        elif "aggressive" in t:
            extracted.risk_profile = "Aggressive"
        elif "moderate" in t or "medium risk" in t:
            extracted.risk_profile = "Moderate"

        if "long term" in t or "long-term" in t:
            extracted.investment_horizon = "Long Term"
        elif "short term" in t or "short-term" in t:
            extracted.investment_horizon = "Short Term"

        if "it stocks" in t or "technology" in t:
            extracted.preferred_sectors.append("IT")
        if "banking" in t or "banks" in t:
            extracted.preferred_sectors.append("Banking")
        if "crypto" in t or "bitcoin" in t:
            extracted.avoided_sectors.append("Crypto")

        return extracted
