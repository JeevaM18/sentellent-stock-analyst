import csv
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.company_service import CompanyService


def load_csv_data(filepath: str) -> list[dict]:
    companies = []
    if not os.path.exists(filepath):
        print(f"Error: CSV file not found at {filepath}")
        return companies

    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies.append({
                "ticker": row["ticker"].strip().upper(),
                "company_name": row["company_name"].strip(),
                "exchange": row.get("exchange", "NSE").strip(),
                "nse_symbol": row.get("nse_symbol", "").strip() or None,
                "bse_symbol": row.get("bse_symbol", "").strip() or None,
                "isin": row.get("isin", "").strip() or None,
                "sector": row.get("sector", "").strip() or None,
                "industry": row.get("industry", "").strip() or None,
                "is_active": True,
            })
    return companies


def run_seeder(db: Session = None) -> tuple[int, int]:
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    csv_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "companies.csv")
    )
    companies_data = load_csv_data(csv_path)

    if not companies_data:
        print("No company records found in CSV.")
        return 0, 0

    print(f"Seeding {len(companies_data)} companies from master CSV...")
    inserted, skipped = CompanyService.seed_companies(db, companies_data)

    print(f"[SUCCESS] Seeding complete: Inserted {inserted} new companies, Skipped {skipped} duplicates.")

    if close_session:
        db.close()

    return inserted, skipped


if __name__ == "__main__":
    run_seeder()
