import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import SessionLocal
from app.models.company import Company
from app.models.company_fundamentals import CompanyFundamentals


def test_crud():
    print("Initializing SQLAlchemy Database Session...")
    db = SessionLocal()

    test_ticker = "TEST_RELIANCE"

    try:
        # Clean up any leftover test data first
        existing = db.query(Company).filter(Company.ticker == test_ticker).first()
        if existing:
            db.delete(existing)
            db.commit()

        # 1. CREATE: Insert sample Company with Fundamentals
        print("\n1. [CREATE] Inserting sample company...")
        test_company = Company(
            ticker=test_ticker,
            company_name="Reliance Industries Test",
            exchange="NSE",
            sector="Energy",
            industry="Oil & Gas",
        )
        db.add(test_company)
        db.commit()
        db.refresh(test_company)

        print(f"   ✓ Created Company ID: {test_company.id}")
        print(f"   ✓ Created At: {test_company.created_at}")

        # Add 1-to-1 Fundamentals
        fundamentals = CompanyFundamentals(
            company_id=test_company.id,
            market_cap=150000000000,
            pe_ratio=24.50,
            eps=102.30,
            roe=15.40,
        )
        db.add(fundamentals)
        db.commit()

        # 2. READ: Query company by ticker
        print("\n2. [READ] Querying company by ticker...")
        queried = db.query(Company).filter(Company.ticker == test_ticker).first()
        assert queried is not None, "Company query failed!"
        print(f"   ✓ Queried Ticker: {queried.ticker}")
        print(f"   ✓ Company Name: {queried.company_name}")
        print(f"   ✓ Sector: {queried.sector}")

        # Test relationship navigation (company.fundamentals)
        assert queried.fundamentals is not None, "Fundamentals relationship failed!"
        print(f"   ✓ Fundamentals PE Ratio: {queried.fundamentals.pe_ratio}")
        print(f"   ✓ Fundamentals Market Cap: ${queried.fundamentals.market_cap:,}")

        # 3. DELETE: Clean up test data
        print("\n3. [DELETE] Cleaning up test data...")
        db.delete(queried)
        db.commit()

        # Verify deletion
        verify_deleted = db.query(Company).filter(Company.ticker == test_ticker).first()
        assert verify_deleted is None, "Deletion failed!"
        print("   ✓ Cleaned up test record successfully.")

        print("\nSUCCESS: All Database Connection, Session Handling, Model Mapping, and CRUD operations verified successfully!")

    except Exception as e:
        db.rollback()
        print(f"\nERROR: CRUD Test failed with error: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    test_crud()
