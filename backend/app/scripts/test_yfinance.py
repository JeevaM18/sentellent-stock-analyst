import os
import sys
from pprint import pprint

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.ingestion.fundamentals import YahooFinanceProvider


def test_provider():
    provider = YahooFinanceProvider()

    for ticker in ["RELIANCE", "TCS", "INFY"]:
        print(f"\n--- Fetching fundamentals for {ticker} ---")
        result = provider.fetch(ticker)
        pprint(result)


if __name__ == "__main__":
    test_provider()
