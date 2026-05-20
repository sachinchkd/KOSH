from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.contribution import Contribution
from app.models.user import User
from app.schemas.dashboard import DashboardSummary, MonthlyPoint

settings = get_settings()
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _previous_months(count: int = 6) -> list[str]:
    today = datetime.utcnow()
    year, month = today.year, today.month
    result: list[str] = []
    for _ in range(count):
        result.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(result))


@router.get("/summary", response_model=DashboardSummary)
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_month = datetime.utcnow().strftime("%Y-%m")
    active_members = db.query(User).filter(User.role == "member", User.is_active.is_(True)).count()

    base_query = db.query(Contribution)
    if current_user.role != "admin":
        base_query = base_query.filter(Contribution.member_id == current_user.id)
        active_members = 1

    total_saved = (
        base_query.with_entities(func.coalesce(func.sum(Contribution.amount), 0))
        .filter(Contribution.status == "approved")
        .scalar()
    )

    current_month_collected = (
        base_query.with_entities(func.coalesce(func.sum(Contribution.amount), 0))
        .filter(Contribution.status == "approved", Contribution.month == current_month)
        .scalar()
    )

    current_month_pending = (
        base_query.with_entities(func.coalesce(func.sum(Contribution.amount), 0))
        .filter(Contribution.status == "pending", Contribution.month == current_month)
        .scalar()
    )

    pending_count = base_query.filter(Contribution.status == "pending").count()

    unpaid_members: list[str] = []
    if current_user.role == "admin":
        members = db.query(User).filter(User.role == "member", User.is_active.is_(True)).order_by(User.name).all()
        for member in members:
            has_paid = (
                db.query(Contribution)
                .filter(
                    Contribution.member_id == member.id,
                    Contribution.month == current_month,
                    Contribution.status == "approved",
                )
                .first()
            )
            if has_paid is None:
                unpaid_members.append(member.name)

    monthly_series: list[MonthlyPoint] = []
    for month in _previous_months(6):
        query = db.query(Contribution).filter(Contribution.month == month)
        if current_user.role != "admin":
            query = query.filter(Contribution.member_id == current_user.id)
        approved_amount = query.with_entities(func.coalesce(func.sum(Contribution.amount), 0)).filter(Contribution.status == "approved").scalar()
        pending_amount = query.with_entities(func.coalesce(func.sum(Contribution.amount), 0)).filter(Contribution.status == "pending").scalar()
        monthly_series.append(
            MonthlyPoint(month=month, approved_amount=int(approved_amount or 0), pending_amount=int(pending_amount or 0))
        )

    return DashboardSummary(
        total_saved=int(total_saved or 0),
        current_month_collected=int(current_month_collected or 0),
        current_month_expected=active_members * settings.monthly_saving_amount,
        current_month_pending=int(current_month_pending or 0),
        pending_count=pending_count,
        active_members=active_members,
        unpaid_members=unpaid_members,
        monthly_series=monthly_series,
    )
