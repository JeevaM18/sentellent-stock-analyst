from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.current_user import get_current_user
from app.models.user import User
from app.schemas.auth import UserResponse, UserSyncPayload
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    """Return authenticated application user verified via Google ID Token."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        profile_picture=current_user.profile_picture,
        created=False,
    )


# TODO: Replace payload-based sync with verified Auth.js token in Phase 3.4.
@router.post(
    "/sync",
    response_model=UserResponse,
)
def sync_user(
    payload: UserSyncPayload,
    db: Session = Depends(get_db),
):
    user, created = AuthService.sync_user(db, payload)

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        profile_picture=user.profile_picture,
        created=created,
    )
