import os
import sys
from pprint import pprint

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.ingestion.news import GoogleNewsRSSProvider


def test_provider():
    provider = GoogleNewsRSSProvider()

    companies = [
        ("Reliance Industries", "RELIANCE"),
        ("Tata Consultancy Services", "TCS"),
        ("Infosys", "INFY"),
    ]

    for company_name, ticker in companies:
        print(f"\n--- Fetching Google News RSS for {company_name} ({ticker}) ---")
        res = provider.fetch(company_name, ticker)

        print("Success:", res["success"])
        print("Total Articles:", len(res["articles"]))

        if res["success"] and res["articles"]:
            print("\nTop 2 Newest Articles:")
            for article in res["articles"][:2]:
                print(f"  • Title: {article['title']}")
                print(f"    Source: {article['source']} | Date: {article['published_at']}")
                print(f"    URL: {article['article_url']}")
                print(f"    Hash: {article['content_hash']}")
                print(f"    Summary: {article['summary'][:120]}...\n")


if __name__ == "__main__":
    test_provider()
