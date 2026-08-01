from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.current_user import get_current_user
from app.models.user import User
from app.schemas.watchlist import (
    FollowCompanyRequest,
    FollowCompanyResponse,
    UnfollowCompanyResponse,
    WatchlistCheckResponse,
    WatchlistCountResponse,
    WatchlistResponse,
)
from app.services.watchlist_service import WatchlistService

router = APIRouter(
    prefix="/api/watchlist",
    tags=["Watchlist"],
)


@router.post(
    "/follow",
    response_model=FollowCompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def follow_company(
    payload: FollowCompanyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a stock to authenticated user's watchlist."""
    watchlist_item = WatchlistService.follow_company(
        db=db,
        user_id=current_user.id,
        company_id=payload.company_id,
    )
    return FollowCompanyResponse(
        message="Company followed successfully",
        watchlist_item=watchlist_item,
    )


@router.delete(
    "/unfollow/{company_id}",
    response_model=UnfollowCompanyResponse,
)
def unfollow_company(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a stock from authenticated user's watchlist."""
    WatchlistService.unfollow_company(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )
    return UnfollowCompanyResponse(
        message="Company unfollowed successfully",
    )


@router.get(
    "",
    response_model=WatchlistResponse,
)
def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve user's watchlist ordered by newest followed stock first."""
    items = WatchlistService.list_watchlist(
        db=db,
        user_id=current_user.id,
    )
    return WatchlistResponse(items=items)


@router.get(
    "/count",
    response_model=WatchlistCountResponse,
)
def get_watchlist_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get total count of companies in user's watchlist."""
    count = WatchlistService.watchlist_count(
        db=db,
        user_id=current_user.id,
    )
    return WatchlistCountResponse(count=count)


@router.get(
    "/check/{company_id}",
    response_model=WatchlistCheckResponse,
)
def check_following_status(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check whether a specific company is in user's watchlist."""
    following = WatchlistService.is_following(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )
    return WatchlistCheckResponse(following=following)
