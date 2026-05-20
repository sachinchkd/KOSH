from pydantic import BaseModel, EmailStr
class GoogleLoginRequest(BaseModel):
    credential: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: str | None = None
    role: str = "member"
    picture: str = ""
    is_active: bool = True
