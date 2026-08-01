import re
import time
import logging
from typing import Any
from sqlalchemy.orm import Session, joinedload

from app.models.company import Company
from app.tools.base import BaseAgentTool

logger = logging.getLogger(__name__)


class FundamentalsTool(BaseAgentTool):
    """
    Advanced Fundamentals Tool executing database lookups and financial reasoning analysis.
    """

    name = "fundamentals"
    description = "Fetches company fundamentals and performs valuation, leverage, and profitability reasoning."

    @classmethod
    def analyze_valuation(cls, pe: float | None, pb: float | None) -> str:
        """Generate financial reasoning for valuation metrics."""
        parts = []
        if pe is not None:
            if pe < 15:
                parts.append(f"Trades at an attractive P/E of {pe:.2f}x (below 15x market value threshold), indicating value pricing.")
            elif pe <= 30:
                parts.append(f"Trades at a moderate P/E of {pe:.2f}x (15x-30x range), indicating fair growth pricing.")
            else:
                parts.append(f"Trades at a premium P/E of {pe:.2f}x (above 30x), reflecting high market growth expectations.")
        else:
            parts.append("P/E ratio data unavailable.")

        if pb is not None:
            if pb < 1.5:
                parts.append(f"P/B of {pb:.2f}x indicates trading near or below book asset value.")
            elif pb <= 4.0:
                parts.append(f"P/B of {pb:.2f}x reflects reasonable asset premium.")
            else:
                parts.append(f"P/B of {pb:.2f}x indicates significant intangible or market premium over book value.")

        return " ".join(parts)

    @classmethod
    def analyze_leverage(cls, de: float | None) -> str:
        """Generate financial reasoning for capital leverage metrics."""
        if de is None:
            return "Debt-to-equity leverage data unavailable."
        if de < 0.5:
            return f"Debt-to-equity ratio of {de:.2f} indicates a conservative balance sheet with low financial leverage risk."
        elif de <= 1.5:
            return f"Debt-to-equity ratio of {de:.2f} reflects manageable debt levels within standard operational bounds."
        else:
            return f"Debt-to-equity ratio of {de:.2f} indicates high leverage and elevated financial risk."

    @classmethod
    def analyze_profitability(cls, roe: float | None, div_yield: float | None) -> str:
        """Generate financial reasoning for profitability and cash distribution metrics."""
        parts = []
        if roe is not None:
            if roe >= 15.0:
                parts.append(f"Strong ROE of {roe:.2f}% indicates high capital efficiency and strong shareholder return generation.")
            elif roe >= 10.0:
                parts.append(f"Moderate ROE of {roe:.2f}% reflects adequate operational profitability.")
            else:
                parts.append(f"ROE of {roe:.2f}% indicates low capital efficiency.")
        else:
            parts.append("ROE metrics unavailable.")

        if div_yield is not None:
            if div_yield >= 2.0:
                parts.append(f"Dividend yield of {div_yield:.2f}% offers attractive cash returns to investors.")
            else:
                parts.append(f"Dividend yield of {div_yield:.2f}% suggests focus on earnings reinvestment.")

        return " ".join(parts)

    def run(self, db: Session | None = None, query: str = "", **kwargs: Any) -> dict[str, Any]:
        """
        Execute database lookup for company fundamentals and compute financial analysis interpretations.
        """
        start_time = time.perf_counter()
        found_company: Company | None = None

        if db and query:
            tokens = [t for t in re.split(r'[\s,\.\?\!]+', query) if len(t) >= 2]
            for token in tokens:
                comp = (
                    db.query(Company)
                    .options(joinedload(Company.fundamentals))
                    .filter(
                        (Company.ticker.ilike(token))
                        | (Company.company_name.ilike(f"%{token}%"))
                    )
                    .first()
                )
                if comp:
                    found_company = comp
                    break

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        if not found_company:
            formatted_context = f"No company fundamental data found in database matching query '{query}'."
            return {
                "status": "not_found",
                "execution_ms": duration_ms,
                "company": None,
                "data": {},
                "analysis": {
                    "valuation": "N/A",
                    "leverage": "N/A",
                    "profitability": "N/A",
                },
                "formatted_context": formatted_context,
            }

        f = getattr(found_company, "fundamentals", None)

        cp = float(f.current_price) if f and getattr(f, "current_price", None) and isinstance(f.current_price, (int, float, str)) and not isinstance(f.current_price, type) else None
        mcap = f.market_cap if f and getattr(f, "market_cap", None) else None
        pe = float(f.pe_ratio) if f and getattr(f, "pe_ratio", None) and isinstance(f.pe_ratio, (int, float, str)) else None
        pb = float(f.price_to_book) if f and getattr(f, "price_to_book", None) and isinstance(f.price_to_book, (int, float, str)) else None
        eps_val = float(f.eps) if f and getattr(f, "eps", None) and isinstance(f.eps, (int, float, str)) else None
        roe_val = float(f.roe) if f and getattr(f, "roe", None) and isinstance(f.roe, (int, float, str)) else None
        dte = float(f.debt_to_equity) if f and getattr(f, "debt_to_equity", None) and isinstance(f.debt_to_equity, (int, float, str)) else None
        div = float(f.dividend_yield) if f and getattr(f, "dividend_yield", None) and isinstance(f.dividend_yield, (int, float, str)) else None
        beta_val = float(f.beta) if f and getattr(f, "beta", None) and isinstance(f.beta, (int, float, str)) else None
        bv = float(f.book_value) if f and getattr(f, "book_value", None) and isinstance(f.book_value, (int, float, str)) else None
        high = float(f.fifty_two_week_high) if f and getattr(f, "fifty_two_week_high", None) and isinstance(f.fifty_two_week_high, (int, float, str)) else None
        low = float(f.fifty_two_week_low) if f and getattr(f, "fifty_two_week_low", None) and isinstance(f.fifty_two_week_low, (int, float, str)) else None

        data = {
            "company_name": str(getattr(found_company, "company_name", "N/A")),
            "ticker": str(getattr(found_company, "ticker", "N/A")),
            "exchange": str(getattr(found_company, "exchange", "NSE")),
            "current_price": cp,
            "market_cap": mcap,
            "pe_ratio": pe,
            "price_to_book": pb,
            "eps": eps_val,
            "roe": roe_val,
            "debt_to_equity": dte,
            "dividend_yield": div,
            "beta": beta_val,
            "book_value": bv,
            "fifty_two_week_high": high,
            "fifty_two_week_low": low,
        }

        # Perform Financial Reasoning Interpretations
        analysis = {
            "valuation": self.analyze_valuation(pe, pb),
            "leverage": self.analyze_leverage(dte),
            "profitability": self.analyze_profitability(roe_val, div),
        }

        mcap_formatted = f"₹{mcap:,}" if isinstance(mcap, (int, float)) else f"₹{mcap}" if mcap is not None else "N/A"

        formatted_lines = [
            f"=== Financial Fundamentals Analysis: {data['company_name']} ({data['ticker']}) ===",
            f"Current Price: ₹{cp}" if cp is not None else "Current Price: N/A",
            f"Market Cap: {mcap_formatted}",
            f"P/E Ratio: {pe:.2f}" if pe is not None else "P/E Ratio: N/A",
            f"P/B Ratio: {pb:.2f}" if pb is not None else "P/B Ratio: N/A",
            f"EPS: ₹{eps_val}" if eps_val is not None else "EPS: N/A",
            f"ROE: {roe_val}%" if roe_val is not None else "ROE: N/A",
            f"Debt to Equity: {dte}" if dte is not None else "Debt to Equity: N/A",
            f"Dividend Yield: {div}%" if div is not None else "Dividend Yield: N/A",
            f"Beta: {beta_val}" if beta_val is not None else "Beta: N/A",
            f"52-Week High: ₹{high}" if high is not None else "52-Week High: N/A",
            f"52-Week Low: ₹{low}" if low is not None else "52-Week Low: N/A",
            "\n--- Financial Reasoning Interpretations ---",
            f"• Valuation Analysis: {analysis['valuation']}",
            f"• Leverage Analysis: {analysis['leverage']}",
            f"• Profitability Analysis: {analysis['profitability']}",
        ]
        formatted_context = "\n".join(formatted_lines)

        return {
            "status": "success",
            "execution_ms": duration_ms,
            "company": data["company_name"],
            "data": data,
            "analysis": analysis,
            "formatted_context": formatted_context,
        }
