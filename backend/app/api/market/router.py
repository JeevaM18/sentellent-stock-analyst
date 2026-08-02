from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.market_data_service import MarketDataService

router = APIRouter(prefix="/api/market", tags=["Market Data"])


@router.get("/indices")
def get_market_indices():
    """Retrieve live NIFTY 50, S&P 500, NASDAQ, and India VIX indices with 3-minute caching."""
    return MarketDataService.get_indices()


@router.get("/mood")
def get_market_mood(db: Session = Depends(get_db)):
    """Retrieve Market Mood score & sentiment index dynamically from PostgreSQL news & momentum."""
    return MarketDataService.get_market_mood(db=db)
