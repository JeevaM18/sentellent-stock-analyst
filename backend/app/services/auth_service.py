from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserSyncPayload


class AuthService:

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def sync_user(db: Session, payload: UserSyncPayload) -> tuple[User, bool]:
        user = AuthService.get_user_by_email(db, payload.email)

        if user:
            user.name = payload.name
            user.profile_picture = payload.picture
            db.commit()
            db.refresh(user)
            return user, False

        user = User(
            google_id=payload.email,
            email=payload.email,
            name=payload.name,
            profile_picture=payload.picture,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user, True
