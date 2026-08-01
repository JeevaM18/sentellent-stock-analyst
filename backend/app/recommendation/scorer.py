import logging
from app.recommendation.constants import (
    FUNDAMENTALS_WEIGHT,
    MEMORY_WEIGHT,
    NEWS_WEIGHT,
    PORTFOLIO_WEIGHT,
    TREND_WEIGHT,
)
from app.recommendation.types import (
    RecommendationCandidate,
    RecommendationEvidence,
    RecommendationReason,
    RecommendationResult,
    RecommendationScore,
)
from app.recommendation.utils import (
    calculate_weighted_score,
    clamp_score,
    risk_alignment,
    sector_match,
)

logger = logging.getLogger(__name__)


class RecommendationScorer:
    """
    Deterministic weighted recommendation scoring engine evaluating Fundamentals (35%),
    News (25%), Memory (20%), Portfolio (10%), and Trend (10%).
    """

    @classmethod
    def score_fundamentals(cls, cand: RecommendationCandidate) -> tuple[float, list[RecommendationReason]]:
        """Evaluate fundamental metrics (PE 20%, ROE 20%, Debt 20%, EPS 15%, Dividend 10%, PB 10%, Beta 5%)."""
        f = cand.fundamentals
        if not f:
            return 50.0, [RecommendationReason(title="Data Missing", description="Fundamentals data unavailable", importance=0.5, category="fundamentals")]

        score = 0.0
        reasons = []

        # 1. P/E Ratio (Max 20 pts)
        pe = f.get("pe_ratio")
        if pe is not None:
            if 10.0 <= pe <= 25.0:
                score += 20.0
                reasons.append(RecommendationReason(title="Fair Valuation", description=f"P/E ratio of {pe:.2f}x indicates attractive growth valuation", importance=0.9, category="fundamentals"))
            elif pe < 10.0:
                score += 15.0
                reasons.append(RecommendationReason(title="Value Stock", description=f"Low P/E of {pe:.2f}x suggests value pricing", importance=0.8, category="fundamentals"))
            elif pe <= 35.0:
                score += 10.0
            else:
                score += 5.0
        else:
            score += 10.0

        # 2. ROE (Max 20 pts)
        roe = f.get("roe")
        if roe is not None:
            if roe >= 15.0:
                score += 20.0
                reasons.append(RecommendationReason(title="High Profitability", description=f"Strong ROE of {roe:.2f}% reflects high capital return efficiency", importance=1.0, category="fundamentals"))
            elif roe >= 10.0:
                score += 12.0
            else:
                score += 5.0
        else:
            score += 10.0

        # 3. Debt to Equity (Max 20 pts)
        de = f.get("debt_to_equity")
        if de is not None:
            if de <= 0.5:
                score += 20.0
                reasons.append(RecommendationReason(title="Conservative Leverage", description=f"Low Debt-to-Equity ratio of {de:.2f} indicates a strong balance sheet", importance=0.9, category="fundamentals"))
            elif de <= 1.2:
                score += 12.0
            else:
                score += 5.0
        else:
            score += 10.0

        # 4. EPS (Max 15 pts)
        eps = f.get("eps")
        if eps is not None and eps > 0:
            score += 15.0
            reasons.append(RecommendationReason(title="Positive Earnings", description=f"Healthy positive EPS of ₹{eps:.2f}", importance=0.8, category="fundamentals"))
        else:
            score += 5.0

        # 5. Dividend Yield (Max 10 pts)
        div = f.get("dividend_yield")
        if div is not None and div >= 1.5:
            score += 10.0
            reasons.append(RecommendationReason(title="Attractive Dividend", description=f"Dividend yield of {div:.2f}% offers cash returns", importance=0.7, category="fundamentals"))
        else:
            score += 5.0

        # 6. P/B Ratio (Max 10 pts)
        pb = f.get("price_to_book")
        if pb is not None and pb <= 3.0:
            score += 10.0
        else:
            score += 5.0

        # 7. Beta (Max 5 pts)
        beta = f.get("beta")
        if beta is not None and beta <= 1.1:
            score += 5.0
        else:
            score += 2.5

        return clamp_score(score), reasons

    @classmethod
    def score_news(cls, cand: RecommendationCandidate) -> tuple[float, list[RecommendationReason]]:
        """Evaluate retrieved news relevance and sentiment."""
        news_items = cand.retrieved_news
        if not news_items:
            return 50.0, []

        max_sim = max((n.get("similarity", 0.0) for n in news_items), default=0.0)
        score = min(max_sim * 100.0, 95.0)

        reasons = []
        if max_sim >= 0.70:
            reasons.append(RecommendationReason(title="Positive News Momentum", description=f"High news relevance score ({max_sim:.2f}) from recent coverage", importance=0.9, category="news"))

        return clamp_score(score), reasons

    @classmethod
    def score_memory(cls, cand: RecommendationCandidate) -> tuple[float, list[RecommendationReason]]:
        """Evaluate alignment with user investor memory (sector, risk, horizon, style)."""
        mem = cand.memory
        if not mem:
            return 70.0, []

        reasons = []

        # Sector score
        pref_sectors = mem.preferred_sectors or []
        avoid_sectors = mem.avoided_sectors or []
        sector_score = sector_match(cand.company.sector, pref_sectors, avoid_sectors)

        if sector_score >= 90.0:
            reasons.append(RecommendationReason(title="Preferred Sector Match", description=f"Operates in user's preferred sector ({cand.company.sector})", importance=1.0, category="memory"))
        elif sector_score == 0.0:
            reasons.append(RecommendationReason(title="Avoided Sector Warning", description=f"Operates in user's avoided sector ({cand.company.sector})", importance=1.0, category="memory"))

        # Risk alignment score
        beta = cand.fundamentals.get("beta")
        risk_score = risk_alignment(beta, mem.risk_profile)
        if risk_score >= 85.0:
            reasons.append(RecommendationReason(title="Risk Profile Alignment", description=f"Stock volatility matches user's {mem.risk_profile} risk profile", importance=0.8, category="memory"))

        overall_mem_score = (sector_score * 0.6) + (risk_score * 0.4)
        return clamp_score(overall_mem_score), reasons

    @classmethod
    def score_portfolio(cls, cand: RecommendationCandidate) -> tuple[float, list[RecommendationReason]]:
        """Evaluate portfolio diversification impact."""
        if cand.in_watchlist:
            # Reward watched stock or promote diversification
            return 85.0, [RecommendationReason(title="Watchlist Holding", description="Stock is already followed in user's portfolio watchlist", importance=0.7, category="portfolio")]
        return 75.0, []

    @classmethod
    def score_trend(cls, cand: RecommendationCandidate) -> tuple[float, list[RecommendationReason]]:
        """Evaluate price trend and earnings momentum."""
        f = cand.fundamentals
        high = f.get("fifty_two_week_high")
        low = f.get("fifty_two_week_low")
        cp = f.get("current_price")

        if high and low and cp and high > low:
            position_in_range = (cp - low) / (high - low)
            if 0.3 <= position_in_range <= 0.8:
                return 85.0, [RecommendationReason(title="Health Price Trend", description="Trading within optimal 52-week price expansion channel", importance=0.6, category="trend")]
            return 70.0, []
        return 65.0, []

    @classmethod
    def evaluate_candidate(cls, cand: RecommendationCandidate) -> RecommendationResult:
        """Execute full evaluation pipeline across all 5 scoring dimensions."""
        f_score, f_reasons = cls.score_fundamentals(cand)
        n_score, n_reasons = cls.score_news(cand)
        m_score, m_reasons = cls.score_memory(cand)
        p_score, p_reasons = cls.score_portfolio(cand)
        t_score, t_reasons = cls.score_trend(cand)

        total_score = calculate_weighted_score(
            fundamental_score=f_score,
            news_score=n_score,
            memory_score=m_score,
            portfolio_score=p_score,
            trend_score=t_score,
        )

        all_reasons = f_reasons + n_reasons + m_reasons + p_reasons + t_reasons

        # Calculate confidence
        confidence = 0.70
        if cand.fundamentals.get("pe_ratio") and cand.fundamentals.get("roe"):
            confidence += 0.15
        if cand.retrieved_news:
            confidence += 0.10
        confidence = round(min(confidence, 0.95), 2)

        score_obj = RecommendationScore(
            fundamental_score=f_score,
            news_score=n_score,
            memory_score=m_score,
            portfolio_score=p_score,
            trend_score=t_score,
            overall_score=total_score,
            confidence=confidence,
        )

        news_titles = [n.get("title", "") for n in cand.retrieved_news]
        memory_matches = [r.description for r in m_reasons]
        citations = [
            {
                "title": n.get("title"),
                "source_url": n.get("source_url"),
                "similarity": n.get("similarity"),
            }
            for n in cand.retrieved_news
        ]

        evidence = RecommendationEvidence(
            news_titles=news_titles,
            fundamental_metrics=cand.fundamentals,
            memory_matches=memory_matches,
            portfolio_analysis="In Watchlist" if cand.in_watchlist else "Diversification Target",
            citations=citations,
        )

        return RecommendationResult(
            company_name=cand.company.company_name,
            ticker=cand.ticker,
            exchange=cand.company.exchange,
            score=score_obj,
            reasons=all_reasons,
            evidence=evidence,
            risk_level=cand.memory.risk_profile if cand.memory and cand.memory.risk_profile else "Moderate",
            expected_horizon=cand.memory.investment_horizon if cand.memory and cand.memory.investment_horizon else "Long Term",
        )
