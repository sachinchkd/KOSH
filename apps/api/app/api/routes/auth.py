from fastapi import APIRouter, Depends, HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.security import create_access_token
from app.schemas.auth import GoogleLoginRequest, MeResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google", response_model=TokenResponse)
def google_login(payload: GoogleLoginRequest):
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_ID is not configured",
        )

    try:
        google_user = id_token.verify_oauth2_token(
            payload.credential,
            google_requests.Request(),
            settings.google_client_id,
             clock_skew_in_seconds=10,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(exc)}",
        )

    email = str(google_user.get("email", "")).strip().lower()
    name = str(google_user.get("name", "")).strip()
    picture = str(google_user.get("picture", "")).strip()
    email_verified = bool(google_user.get("email_verified"))

    if not email or not email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account email is not verified",
        )

    role = "member"

    if email in settings.google_admin_email_list:
        role = "admin"

    access_token = create_access_token(
        subject=email,
        extra={
            "email": email,
            "name": name,
            "role": role,
            "picture": picture,
        },
    )

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=MeResponse)
def me(current_user=Depends(get_current_user)):
    return current_user