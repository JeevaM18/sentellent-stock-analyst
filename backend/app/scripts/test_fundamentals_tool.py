"""
CLI verification script for Phase 7.4 — Advanced Fundamentals Tool with Financial Reasoning.

Usage:
    cd backend
    python app/scripts/test_fundamentals_tool.py
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.db.database import SessionLocal
from app.tools.fundamentals import FundamentalsTool


def test_query(db, tool: FundamentalsTool, query: str):
    print("=" * 65)
    print(f"Advanced Fundamentals Tool Execution: Query = '{query}'")
    print("=" * 65)

    res = tool.run(db=db, query=query)
    status_str = res.get("status", "unknown").upper()
    exec_ms = res.get("execution_ms", 0.0)
    company_name = res.get("company")
    data = res.get("data", {})
    analysis = res.get("analysis", {})

    print(f"\nStatus         : {status_str}")
    print(f"Execution Time : {exec_ms:.2f} ms")

    if status_str == "SUCCESS":
        print(f"Company        : {company_name} ({data.get('ticker')})")

        print("\n" + "-" * 65)
        print("Raw Financial Metrics:")
        print(f"  Current Price : ₹{data.get('current_price')}" if data.get('current_price') else "  Current Price : N/A")
        print(f"  P/E Ratio     : {data.get('pe_ratio')}" if data.get('pe_ratio') else "  P/E Ratio     : N/A")
        print(f"  ROE           : {data.get('roe')}%" if data.get('roe') else "  ROE           : N/A")
        print(f"  Dividend Yield: {data.get('dividend_yield')}%" if data.get('dividend_yield') else "  Dividend Yield: N/A")

        print("\n" + "-" * 65)
        print("Financial Reasoning Interpretations:")
        print(f"  Valuation    : {analysis.get('valuation')}")
        print(f"  Leverage     : {analysis.get('leverage')}")
        print(f"  Profitability: {analysis.get('profitability')}")

        print("\n" + "-" * 65)
        print("Formatted Context Output:\n")
        print(res.get("formatted_context"))
    else:
        print(f"Notice         : {res.get('formatted_context')}")

    print("=" * 65)


def main():
    db = SessionLocal()
    try:
        tool = FundamentalsTool()

        # Test 1: Real Company Lookup & Financial Reasoning
        test_query(db, tool, "Reliance")

        print("\n\n")

        # Test 2: Error Handling / Unknown Company Lookup
        test_query(db, tool, "XYZ_UNKNOWN_COMPANY")

        print("\n[OK] Advanced Fundamentals Tool database integration verification complete!")

    finally:
        db.close()


if __name__ == "__main__":
    main()
