from datetime import datetime

from pydantic import BaseModel, Field


class ContributionOut(BaseModel):
    id: int
    member_id: int
    member_name: str
    month: str
    amount: int
    payment_method: str
    status: str
    photo_url: str | None = None
    remarks: str | None = None
    submitted_at: datetime
    approved_at: datetime | None = None
    approved_by_name: str | None = None
    google_sheet_row_id: str | None = None


class ContributionStatusUpdate(BaseModel):
    remarks: str | None = None


class ContributionCreateJson(BaseModel):
    member_id: int | None = None
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    amount: int = 1000
    payment_method: str = "Cash"
    remarks: str | None = None
