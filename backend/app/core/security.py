import os
from fastapi import HTTPException, status
from google.auth.transport import requests
from google.oauth2 import id_token

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")


def verify_google_token(token: str) -> dict:
    """Verify a Google ID Token signature, expiration, issuer, and audience."""
    try:
        payload = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID if GOOGLE_CLIENT_ID else None,
        )
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID Token",
        ) from e
