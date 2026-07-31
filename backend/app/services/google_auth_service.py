from app.core.security import verify_google_token
from app.schemas.auth import UserSyncPayload


class GoogleAuthService:

    @staticmethod
    def get_google_user_claims(token: str) -> UserSyncPayload:
        """Verify Google ID Token and extract validated user claims."""
        claims = verify_google_token(token)
        return UserSyncPayload(
            email=claims.get("email"),
            name=claims.get("name", claims.get("email")),
            picture=claims.get("picture"),
        )
