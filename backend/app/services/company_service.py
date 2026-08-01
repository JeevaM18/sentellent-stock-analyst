from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.company import Company
from app.schemas.company import CompanyBase


class CompanyService:

    @staticmethod
    def get_company_by_id(db: Session, company_id: UUID) -> Company | None:
        return db.query(Company).filter(Company.id == company_id).first()

    @staticmethod
    def get_company_by_ticker(db: Session, ticker: str) -> Company | None:
        return db.query(Company).filter(Company.ticker == ticker.upper()).first()

    @staticmethod
    def get_active_companies(db: Session) -> list[Company]:
        """Retrieve list of active listed companies ordered by ticker."""
        return (
            db.query(Company)
            .filter(Company.is_active.is_(True))
            .order_by(Company.ticker)
            .all()
        )

    @staticmethod
    def search_companies(
        db: Session,
        search: str | None = None,
        sector: str | None = None,
        exchange: str | None = None,
        is_active: bool | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Company], int]:
        query = db.query(Company)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Company.ticker.ilike(search_pattern),
                    Company.company_name.ilike(search_pattern),
                    Company.nse_symbol.ilike(search_pattern),
                    Company.bse_symbol.ilike(search_pattern),
                )
            )

        if sector:
            query = query.filter(Company.sector.ilike(sector))

        if exchange:
            query = query.filter(Company.exchange.ilike(exchange))

        if is_active is not None:
            query = query.filter(Company.is_active == is_active)

        total = query.count()
        offset = (page - 1) * limit
        companies = query.order_by(Company.ticker).offset(offset).limit(limit).all()

        return companies, total

    @staticmethod
    def create_company(db: Session, data: CompanyBase) -> Company:
        company = Company(
            ticker=data.ticker.upper(),
            company_name=data.company_name,
            exchange=data.exchange,
            nse_symbol=data.nse_symbol,
            bse_symbol=data.bse_symbol,
            isin=data.isin,
            sector=data.sector,
            industry=data.industry,
            is_active=data.is_active,
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    @staticmethod
    def seed_companies(db: Session, companies_data: list[dict]) -> tuple[int, int]:
        """Idempotent batch seeder for inserting company master records efficiently."""
        existing_tickers = {c.ticker for c in db.query(Company.ticker).all()}
        new_companies = []
        skipped_count = 0

        for item in companies_data:
            ticker = item["ticker"].upper()
            if ticker in existing_tickers:
                skipped_count += 1
                continue

            existing_tickers.add(ticker)
            new_companies.append(
                Company(
                    ticker=ticker,
                    company_name=item["company_name"],
                    exchange=item.get("exchange", "NSE"),
                    nse_symbol=item.get("nse_symbol"),
                    bse_symbol=item.get("bse_symbol"),
                    isin=item.get("isin"),
                    sector=item.get("sector"),
                    industry=item.get("industry"),
                    is_active=item.get("is_active", True),
                )
            )

        if new_companies:
            db.bulk_save_objects(new_companies)
            db.commit()

        return len(new_companies), skipped_count
