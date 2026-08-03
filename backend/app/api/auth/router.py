from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
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

DEMO_PROFILES = {
    "hari": {
        "email": "hari.demo@sentellent.ai",
        "name": "Hari Sankar",
        "profile_picture": "https://api.dicebear.com/7.x/avataaars/svg?seed=Felix",
    },
    "naga": {
        "email": "naga.demo@sentellent.ai",
        "name": "Naga",
        "profile_picture": "https://api.dicebear.com/7.x/avataaars/svg?seed=Christopher",
    },
}


class DemoLoginPayload(BaseModel):
    demo_user: str


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    """Return authenticated application user verified via Google ID Token or Demo Session."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        profile_picture=current_user.profile_picture,
        created=False,
    )


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


@router.post(
    "/demo-login",
    response_model=UserResponse,
)
def demo_login(
    payload: DemoLoginPayload,
    db: Session = Depends(get_db),
):
    """
    Authenticate predefined evaluator demo profiles without requiring Google OAuth consent.
    Automatically provisions/fetches the user in PostgreSQL and returns an active user session.
    """
    key = payload.demo_user.lower().strip()
    profile = DEMO_PROFILES.get(key)

    if not profile:
        if "naga" in key:
            profile = DEMO_PROFILES["naga"]
        elif "hari" in key:
            profile = DEMO_PROFILES["hari"]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown demo user profile: {payload.demo_user}. Supported: 'hari', 'naga'",
            )

    sync_payload = UserSyncPayload(
        email=profile["email"],
        name=profile["name"],
        profile_picture=profile["profile_picture"],
    )
    user, created = AuthService.sync_user(db, sync_payload)

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        profile_picture=user.profile_picture,
        created=created,
    )
