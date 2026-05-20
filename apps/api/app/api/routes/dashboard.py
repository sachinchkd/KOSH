from datetime import datetime

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.deps import get_current_user
from app.schemas.dashboard import DashboardSummary, MonthlyPoint
from app.services.google import read_sheet_rows

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


def _text(value) -> str:
    return str(value or "").strip()


def _lower(value) -> str:
    return _text(value).lower()


def _amount(value) -> int:
    try:
        return int(float(_text(value).replace(",", "")))
    except ValueError:
        return 0


def _is_active_member(row: dict) -> bool:
    status = _lower(row.get("Status", "Active"))
    return status in {"active", "true", "yes", "1"}


def _member_email(row: dict) -> str:
    return _lower(row.get("Email"))


def _contribution_email(row: dict) -> str:
    return _lower(row.get("Member Email"))


def _contribution_month(row: dict) -> str:
    return _text(row.get("Month"))


def _contribution_status(row: dict) -> str:
    return _lower(row.get("Status"))


@router.get("/summary", response_model=DashboardSummary)
def summary(current_user=Depends(get_current_user)):
    current_month = datetime.utcnow().strftime("%Y-%m")

    members = read_sheet_rows("Members")
    contributions = read_sheet_rows("Contributions")

    active_member_rows = [row for row in members if _is_active_member(row)]

    if current_user.role != "admin":
        contributions = [
            row
            for row in contributions
            if _contribution_email(row) == current_user.email.lower()
        ]
        active_members = 1
    else:
        active_members = len(active_member_rows)

        if active_members == 0:
            unique_emails = {
                _contribution_email(row)
                for row in contributions
                if _contribution_email(row)
            }
            active_members = len(unique_emails)

    approved_rows = [
        row
        for row in contributions
        if _contribution_status(row) == "approved"
    ]

    pending_rows = [
        row
        for row in contributions
        if _contribution_status(row) == "pending"
    ]

    total_saved = sum(_amount(row.get("Amount")) for row in approved_rows)

    current_month_collected = sum(
        _amount(row.get("Amount"))
        for row in approved_rows
        if _contribution_month(row) == current_month
    )

    current_month_pending = sum(
        _amount(row.get("Amount"))
        for row in pending_rows
        if _contribution_month(row) == current_month
    )

    unpaid_members: list[str] = []

    if current_user.role == "admin":
        paid_emails = {
            _contribution_email(row)
            for row in approved_rows
            if _contribution_month(row) == current_month
        }

        for member in active_member_rows:
            email = _member_email(member)
            name = _text(member.get("Name")) or email

            if email and email not in paid_emails:
                unpaid_members.append(name)

    monthly_series: list[MonthlyPoint] = []

    for month in _previous_months(6):
        approved_amount = sum(
            _amount(row.get("Amount"))
            for row in contributions
            if _contribution_month(row) == month
            and _contribution_status(row) == "approved"
        )

        pending_amount = sum(
            _amount(row.get("Amount"))
            for row in contributions
            if _contribution_month(row) == month
            and _contribution_status(row) == "pending"
        )

        monthly_series.append(
            MonthlyPoint(
                month=month,
                approved_amount=approved_amount,
                pending_amount=pending_amount,
            )
        )

    return DashboardSummary(
        total_saved=total_saved,
        current_month_collected=current_month_collected,
        current_month_expected=active_members * settings.monthly_saving_amount,
        current_month_pending=current_month_pending,
        pending_count=len(pending_rows),
        active_members=active_members,
        unpaid_members=unpaid_members,
        monthly_series=monthly_series,
    )