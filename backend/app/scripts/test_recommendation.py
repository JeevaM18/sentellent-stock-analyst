"""
CLI verification script for Phase 9 — Recommendation Engine (Personalized AI Investment Advisor).

Usage:
    cd backend
    python app/scripts/test_recommendation.py
"""
import sys
import os
import uuid
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.models.company import Company
from app.models.investor_memory import InvestorMemory
from app.recommendation.candidate_builder import RecommendationCandidateBuilder
from app.recommendation.ranking import RecommendationRanker
from app.recommendation.scorer import RecommendationScorer
from app.recommendation.types import RecommendationCandidate


def main():
    print("=" * 65)
    print("Phase 9 — Recommendation Engine Verification & Weighted Scoring")
    print("=" * 65)

    # 1. Mock Investor Memory
    memory = InvestorMemory(
        risk_profile="Moderate",
        investment_horizon="Long Term",
        preferred_sectors=["IT", "Banking"],
        avoided_sectors=["Crypto"],
        confidence_score=0.90,
    )

    # 2. Mock Companies & Candidates
    comp1 = Company(id=uuid.uuid4(), company_name="Tata Consultancy Services", ticker="TCS", exchange="NSE", sector="IT")
    comp2 = Company(id=uuid.uuid4(), company_name="ICICI Bank", ticker="ICICIBANK", exchange="NSE", sector="Banking")
    comp3 = Company(id=uuid.uuid4(), company_name="Reliance Industries", ticker="RELIANCE", exchange="NSE", sector="Energy")

    cand1 = RecommendationCandidate(
        company=comp1,
        ticker="TCS",
        company_id=comp1.id,
        fundamentals={"pe_ratio": 24.5, "roe": 38.0, "debt_to_equity": 0.08, "eps": 120.0, "dividend_yield": 2.2, "beta": 0.8},
        retrieved_news=[{"title": "TCS reports 12% profit growth", "similarity": 0.88}],
        memory=memory,
    )

    cand2 = RecommendationCandidate(
        company=comp2,
        ticker="ICICIBANK",
        company_id=comp2.id,
        fundamentals={"pe_ratio": 17.2, "roe": 18.5, "debt_to_equity": 0.45, "eps": 65.0, "dividend_yield": 1.2, "beta": 1.0},
        retrieved_news=[{"title": "ICICI Bank Q1 credit growth surges", "similarity": 0.82}],
        memory=memory,
    )

    cand3 = RecommendationCandidate(
        company=comp3,
        ticker="RELIANCE",
        company_id=comp3.id,
        fundamentals={"pe_ratio": 26.0, "roe": 12.0, "debt_to_equity": 0.65, "eps": 95.0, "dividend_yield": 0.8, "beta": 1.15},
        retrieved_news=[{"title": "Reliance green energy expansion update", "similarity": 0.75}],
        memory=memory,
    )

    candidates = [cand1, cand2, cand3]

    print(f"\n--- [1] Evaluating {len(candidates)} Candidates via Weighted Scoring Engine ---")
    results = [RecommendationScorer.evaluate_candidate(cand) for cand in candidates]

    # Rank
    top_ranked = RecommendationRanker.top_k(results, k=3)

    print("\n" + "=" * 65)
    print("Personalized Recommendation Results:")
    print("=" * 65)

    for idx, r in enumerate(top_ranked, 1):
        s = r.score
        print(f"\n{idx}. {r.company_name} ({r.ticker})")
        print(f"   Overall Score : {s.overall_score:.1f} / 100  (Confidence: {s.confidence:.2f})")
        print(f"   Fundamentals  : {s.fundamental_score:.1f}")
        print(f"   News Relevance: {s.news_score:.1f}")
        print(f"   Memory Match  : {s.memory_score:.1f}")
        print(f"   Portfolio     : {s.portfolio_score:.1f}")
        print(f"   Trend         : {s.trend_score:.1f}")
        print("   Key Reasons:")
        for reason in r.reasons[:3]:
            print(f"     ✔ {reason.title}: {reason.description}")

    print("\n" + "=" * 65)
    print("[OK] Recommendation Engine verification complete!")


if __name__ == "__main__":
    main()
