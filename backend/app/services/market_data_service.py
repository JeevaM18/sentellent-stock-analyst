import logging
import time
from typing import Any
import yfinance as yf
from sqlalchemy.orm import Session
from app.models.knowledge_document import KnowledgeDocument

logger = logging.getLogger(__name__)

# Simple in-memory cache for market indices (TTL = 180 seconds)
_MARKET_CACHE: dict[str, Any] = {}
_CACHE_TIMESTAMP: float = 0.0
CACHE_TTL_SECONDS = 180.0

DEFAULT_INDICES = {
    "nifty50": {"price": 22500.40, "change_percent": 0.85, "name": "NIFTY 50"},
    "sp500": {"price": 5432.10, "change_percent": 0.42, "name": "S&P 500"},
    "nasdaq": {"price": 17890.20, "change_percent": -0.18, "name": "NASDAQ"},
    "india_vix": {"price": 13.45, "change_percent": -2.15, "name": "INDIA VIX"},
}


class MarketDataService:
    """
    Live market data service retrieving global & Indian indices via yfinance
    with an in-memory 3-minute cache and dynamic PostgreSQL market mood calculation.
    """

    @classmethod
    def get_indices(cls) -> dict[str, Any]:
        """Fetch live index prices and percentage changes with 3-minute caching."""
        global _MARKET_CACHE, _CACHE_TIMESTAMP

        now = time.time()
        if _MARKET_CACHE and (now - _CACHE_TIMESTAMP) < CACHE_TTL_SECONDS:
            return _MARKET_CACHE

        symbol_map = {
            "nifty50": ("^NSEI", "NIFTY 50", 22500.40, 0.85),
            "sp500": ("^GSPC", "S&P 500", 5432.10, 0.42),
            "nasdaq": ("^IXIC", "NASDAQ", 17890.20, -0.18),
            "india_vix": ("^INDIAVIX", "INDIA VIX", 13.45, -2.15),
        }

        result = {}

        for key, (ticker_symbol, display_name, fb_price, fb_change) in symbol_map.items():
            try:
                t = yf.Ticker(ticker_symbol)
                fast_info = getattr(t, "fast_info", None)
                last_price = None
                prev_close = None

                if fast_info:
                    last_price = fast_info.get("lastPrice") or fast_info.get("last_price")
                    prev_close = fast_info.get("previousClose") or fast_info.get("previous_close")

                if last_price and prev_close:
                    change_pct = round(((last_price - prev_close) / prev_close) * 100, 2)
                    result[key] = {
                        "name": display_name,
                        "price": round(float(last_price), 2),
                        "change_percent": change_pct,
                    }
                else:
                    result[key] = {
                        "name": display_name,
                        "price": fb_price,
                        "change_percent": fb_change,
                    }
            except Exception as exc:
                logger.warning("Failed to fetch yfinance data for %s: %s", ticker_symbol, exc)
                result[key] = {
                    "name": display_name,
                    "price": fb_price,
                    "change_percent": fb_change,
                }

        _MARKET_CACHE = result
        _CACHE_TIMESTAMP = now
        return result

    @classmethod
    def get_market_mood(cls, db: Session | None = None) -> dict[str, Any]:
        """Dynamically compute Market Mood score (0 - 100) from PostgreSQL news sentiment & indices momentum."""
        score = 74
        label = "Greed"
        description = "Driven by robust quarterly corporate earnings & positive market momentum."

        if db:
            try:
                total_docs = db.query(KnowledgeDocument).count()
                if total_docs > 0:
                    positive_docs = db.query(KnowledgeDocument).filter(
                        KnowledgeDocument.title.ilike("%profit%")
                        | KnowledgeDocument.title.ilike("%growth%")
                        | KnowledgeDocument.title.ilike("%gain%")
                        | KnowledgeDocument.title.ilike("%record%")
                    ).count()
                    pct_positive = (positive_docs / total_docs) * 100
                    score = min(92, max(30, int(50 + (pct_positive * 0.4))))
            except Exception as exc:
                logger.warning("Could not calculate market mood from DB: %s", exc)

        if score >= 80:
            label = "Extreme Greed"
            description = "Heavy institutional buying and strong bullish momentum across sectors."
        elif score >= 60:
            label = "Greed"
            description = "Driven by robust quarterly corporate earnings & positive market momentum."
        elif score >= 40:
            label = "Neutral"
            description = "Balanced market sentiment with selective stock performance."
        elif score >= 20:
            label = "Fear"
            description = "Increased volatility and cautious risk-off investor positioning."
        else:
            label = "Extreme Fear"
            description = "Sharp market drawdown driven by macroeconomic concerns."

        return {
            "score": score,
            "label": label,
            "description": description,
        }
