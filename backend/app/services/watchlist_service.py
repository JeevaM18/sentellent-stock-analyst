from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.models.company import Company
from app.models.user_followed_stock import UserFollowedStock
from app.schemas.watchlist import WatchlistItemResponse
from app.services.company_service import CompanyService


class WatchlistService:

    @staticmethod
    def is_following(db: Session, user_id: UUID, company_id: UUID) -> bool:
        """Check if user follows a specific company."""
        record = (
            db.query(UserFollowedStock)
            .filter(
                UserFollowedStock.user_id == user_id,
                UserFollowedStock.company_id == company_id,
            )
            .first()
        )
        return record is not None

    @staticmethod
    def follow_company(
        db: Session, user_id: UUID, company_id: UUID
    ) -> WatchlistItemResponse:
        """Add a company to user's watchlist."""
        company = db.query(Company).options(selectinload(Company.fundamentals)).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID '{company_id}' not found",
            )

        if WatchlistService.is_following(db, user_id, company_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Company '{company.ticker}' is already in your watchlist",
            )

        followed = UserFollowedStock(user_id=user_id, company_id=company_id)
        db.add(followed)
        db.commit()
        db.refresh(followed)

        return WatchlistItemResponse(
            company_id=company.id,
            ticker=company.ticker,
            company_name=company.company_name,
            exchange=company.exchange,
            sector=company.sector,
            followed_at=followed.followed_at,
            following=True,
            company=company,
        )

    @staticmethod
    def unfollow_company(db: Session, user_id: UUID, company_id: UUID) -> bool:
        """Remove a company from user's watchlist."""
        record = (
            db.query(UserFollowedStock)
            .filter(
                UserFollowedStock.user_id == user_id,
                UserFollowedStock.company_id == company_id,
            )
            .first()
        )
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company is not in your watchlist",
            )

        db.delete(record)
        db.commit()
        return True

    @staticmethod
    def list_watchlist(db: Session, user_id: UUID) -> list[WatchlistItemResponse]:
        """Retrieve user's watchlist ordered by newest followed stock first."""
        records = (
            db.query(UserFollowedStock, Company)
            .join(Company, UserFollowedStock.company_id == Company.id)
            .options(selectinload(Company.fundamentals))
            .filter(UserFollowedStock.user_id == user_id)
            .order_by(UserFollowedStock.followed_at.desc())
            .all()
        )

        if not records:
            # Auto-seed top companies (RELIANCE, TCS, HDFCBANK) if user watchlist is empty
            top_comps = db.query(Company).filter(Company.ticker.in_(["RELIANCE", "TCS", "HDFCBANK"])).all()
            for comp in top_comps:
                db.add(UserFollowedStock(user_id=user_id, company_id=comp.id))
            db.commit()

            records = (
                db.query(UserFollowedStock, Company)
                .join(Company, UserFollowedStock.company_id == Company.id)
                .options(selectinload(Company.fundamentals))
                .filter(UserFollowedStock.user_id == user_id)
                .order_by(UserFollowedStock.followed_at.desc())
                .all()
            )

        return [
            WatchlistItemResponse(
                company_id=company.id,
                ticker=company.ticker,
                company_name=company.company_name,
                exchange=company.exchange,
                sector=company.sector,
                followed_at=followed.followed_at,
                following=True,
                company=company,
            )
            for followed, company in records
        ]

    @staticmethod
    def watchlist_count(db: Session, user_id: UUID) -> int:
        """Return total count of companies in user's watchlist."""
        return (
            db.query(UserFollowedStock)
            .filter(UserFollowedStock.user_id == user_id)
            .count()
        )

    @staticmethod
    def get_followed_company_ids(db: Session, user_id: UUID) -> list[UUID]:
        """Return list of company UUIDs followed by the user."""
        records = (
            db.query(UserFollowedStock.company_id)
            .filter(UserFollowedStock.user_id == user_id)
            .all()
        )
        return [r[0] for r in records]

    @staticmethod
    def get_followed_companies(db: Session, user_id: UUID) -> list[Company]:
        """Return list of Company models followed by the user."""
        return (
            db.query(Company)
            .join(UserFollowedStock, Company.id == UserFollowedStock.company_id)
            .options(selectinload(Company.fundamentals))
            .filter(UserFollowedStock.user_id == user_id)
            .order_by(Company.ticker)
            .all()
        )
