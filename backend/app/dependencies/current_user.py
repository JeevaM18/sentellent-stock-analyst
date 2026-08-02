from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.google_auth_service import GoogleAuthService


def get_current_user(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """Dependency to extract Bearer token, verify Google identity, sync user, and return User model."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Authorization header",
        )

    token = authorization.split(" ")[1]

    # Developer / demo mode fallback token
    if token == "dev-sentellent-auth-token":
        default_user = db.query(User).filter(User.email == "jeeva@sentellent.ai").first()
        if not default_user:
            default_user = db.query(User).first()
        if not default_user:
            default_user = User(email="jeeva@sentellent.ai", name="Jeeva M")
            db.add(default_user)
            db.commit()
            db.refresh(default_user)
        return default_user

    claims = GoogleAuthService.get_google_user_claims(token)
    user, _ = AuthService.sync_user(db, claims)
    return user


def get_optional_current_user(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
) -> User | None:
    """Optional dependency returning User model if Bearer token present, or None if unauthenticated."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        return get_current_user(authorization=authorization, db=db)
    except Exception:
        return None
