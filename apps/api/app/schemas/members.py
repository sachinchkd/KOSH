from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class MemberCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=8)
    role: str = "member"


class MemberUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    is_active: bool | None = None


class MemberOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None = None
    role: str
    joined_at: datetime
    is_active: bool
    total_paid: int = 0

    model_config = {"from_attributes": True}
