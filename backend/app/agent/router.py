from enum import Enum
import re
import logging

from app.agent.intent_keywords import (
    COMBINED_KEYWORDS,
    FUNDAMENTALS_KEYWORDS,
    RETRIEVAL_KEYWORDS,
    WATCHLIST_KEYWORDS,
)

logger = logging.getLogger(__name__)


class IntentType(str, Enum):
    """Enumeration of agent query intent categories."""
    RETRIEVAL = "retrieval"
    FUNDAMENTALS = "fundamentals"
    WATCHLIST = "watchlist"
    COMBINED = "combined"
    UNKNOWN = "unknown"


class IntentRouter:
    """Router classifying question intent into specialized execution branches."""

    @staticmethod
    def classify(question: str) -> IntentType:
        """Classify user query string into an IntentType."""
        if not question or not question.strip():
            return IntentType.UNKNOWN

        q_clean = question.lower().strip()

        # Check for Watchlist keywords
        for kw in WATCHLIST_KEYWORDS:
            if kw in q_clean:
                # If watchlist + news/fundamentals, classify as combined
                for fkw in FUNDAMENTALS_KEYWORDS:
                    if fkw in q_clean:
                        return IntentType.COMBINED
                for rkw in RETRIEVAL_KEYWORDS:
                    if rkw in q_clean:
                        return IntentType.COMBINED
                return IntentType.WATCHLIST

        # Check for Combined explicit triggers
        for kw in COMBINED_KEYWORDS:
            if kw in q_clean:
                return IntentType.COMBINED

        # Check for Fundamentals keywords (using regex word boundary for short abbreviations like 'pe')
        for kw in FUNDAMENTALS_KEYWORDS:
            pattern = r'\b' + re.escape(kw) + r'\b' if len(kw) <= 4 else re.escape(kw)
            if re.search(pattern, q_clean):
                return IntentType.FUNDAMENTALS

        # Default fallback is Semantic Retrieval
        return IntentType.RETRIEVAL

    @staticmethod
    def route(question: str) -> str:
        """Return the target node name for graph conditional routing."""
        intent = IntentRouter.classify(question)
        if intent == IntentType.FUNDAMENTALS:
            return "fundamentals"
        elif intent == IntentType.WATCHLIST:
            return "watchlist"
        else:
            return "retrieve"
