from abc import ABC, abstractmethod
from datetime import datetime, timezone
import time
from typing import Any
import yfinance as yf

from .constants import MAX_RETRIES, RETRY_DELAY_SECONDS, YAHOO_SUFFIX


class BaseFundamentalsProvider(ABC):
    """Abstract interface for financial fundamentals data providers."""

    @abstractmethod
    def fetch(self, ticker: str) -> dict[str, Any]:
        """Fetch and normalize financial fundamentals for a given stock ticker."""
        pass


class YahooFinanceProvider(BaseFundamentalsProvider):
    """
    Resilient fundamentals provider utilizing yfinance with automatic retries,
    data validation, and metadata logging envelopes.
    """

    def fetch(self, ticker: str) -> dict[str, Any]:
        clean_ticker = ticker.strip().upper()
        symbol = f"{clean_ticker}{YAHOO_SUFFIX}" if not clean_ticker.endswith(".NS") and not clean_ticker.endswith(".BO") else clean_ticker

        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                stock = yf.Ticker(symbol)
                info = stock.info

                # Validate response is non-empty and contains valid price data
                current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
                if not info or current_price is None:
                    raise ValueError(f"Yahoo Finance returned empty or invalid info dict for {symbol}")

                normalized_data = {
                    "current_price": current_price,
                    "market_cap": info.get("marketCap"),
                    "shares_outstanding": info.get("sharesOutstanding"),
                    "pe_ratio": info.get("trailingPE"),
                    "eps": info.get("trailingEps"),
                    "roe": info.get("returnOnEquity"),
                    "debt_to_equity": info.get("debtToEquity"),
                    "dividend_yield": info.get("dividendYield"),
                    "book_value": info.get("bookValue"),
                    "price_to_book": info.get("priceToBook"),
                    "beta": info.get("beta"),
                    "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                    "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                    "currency": info.get("currency", "INR"),
                }

                return {
                    "success": True,
                    "ticker": clean_ticker,
                    "provider": "Yahoo Finance",
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    "data": normalized_data,
                }

            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS)

        return {
            "success": False,
            "ticker": clean_ticker,
            "provider": "Yahoo Finance",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "error": str(last_error) if last_error else "Failed to retrieve stock fundamentals",
        }
