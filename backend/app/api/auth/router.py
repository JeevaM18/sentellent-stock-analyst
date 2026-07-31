from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import UserResponse, UserSyncPayload
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
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
