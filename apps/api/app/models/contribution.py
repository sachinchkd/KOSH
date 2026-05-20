from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Contribution(Base):
    __tablename__ = "contributions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)  # YYYY-MM
    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    payment_method: Mapped[str] = mapped_column(String(40), nullable=False, default="Cash")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    google_sheet_row_id: Mapped[str | None] = mapped_column(String(120), nullable=True)

    member = relationship("User", foreign_keys=[member_id], back_populates="contributions")
    approved_by = relationship("User", foreign_keys=[approved_by_id])
