from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr

from app.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/google")


class CurrentUser(BaseModel):
    id: str
    email: EmailStr
    name: str = ""
    role: str = "member"
    picture: str = ""
    is_active: bool = True


def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    email = payload.get("sub")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    return CurrentUser(
        id=str(email),
        email=str(email),
        name=str(payload.get("name", "")),
        role=str(payload.get("role", "member")),
        picture=str(payload.get("picture", "")),
        is_active=True,
    )


def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user