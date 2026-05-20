from datetime import datetime

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.deps import get_current_user
from app.services.google import read_sheet_rows

router = APIRouter(prefix="/reports", tags=["reports"])


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
    return _lower(row.get("Status", "Active")) in {"active", "true", "yes", "1"}


def _member_email(row: dict) -> str:
    return _lower(row.get("Email"))


def _contribution_email(row: dict) -> str:
    return _lower(row.get("Member Email"))


def _contribution_status(row: dict) -> str:
    return _lower(row.get("Status"))


def _contribution_month(row: dict) -> str:
    return _text(row.get("Month"))


@router.get("/monthly")
def monthly_report(
    month: str | None = None,
    current_user=Depends(get_current_user),
):
    report_month = month or datetime.utcnow().strftime("%Y-%m")

    members = read_sheet_rows("Members")
    contributions = read_sheet_rows("Contributions")

    active_members = [row for row in members if _is_active_member(row)]

    if current_user.role != "admin":
        contributions = [
            row
            for row in contributions
            if _contribution_email(row) == current_user.email.lower()
        ]

        active_members = [
            row
            for row in active_members
            if _member_email(row) == current_user.email.lower()
        ]

        if not active_members:
            active_members = [
                {
                    "Name": current_user.name or current_user.email,
                    "Email": current_user.email,
                    "Status": "Active",
                }
            ]

    month_rows = [
        row
        for row in contributions
        if _contribution_month(row) == report_month
    ]

    approved_rows = [
        row
        for row in month_rows
        if _contribution_status(row) == "approved"
    ]

    pending_rows = [
        row
        for row in month_rows
        if _contribution_status(row) == "pending"
    ]

    rejected_rows = [
        row
        for row in month_rows
        if _contribution_status(row) == "rejected"
    ]

    paid_emails = {
        _contribution_email(row)
        for row in approved_rows
        if _contribution_email(row)
    }

    unpaid_members = []

    for member in active_members:
        email = _member_email(member)
        name = _text(member.get("Name")) or email

        if email and email not in paid_emails:
            unpaid_members.append(name)

    expected_amount = len(active_members) * settings.monthly_saving_amount
    collected_amount = sum(_amount(row.get("Amount")) for row in approved_rows)
    pending_amount = sum(_amount(row.get("Amount")) for row in pending_rows)

    return {
        "month": report_month,
        "expected_amount": expected_amount,
        "collected_amount": collected_amount,
        "pending_amount": pending_amount,
        "remaining_amount": max(expected_amount - collected_amount, 0),
        "active_members": len(active_members),
        "paid_members": len(paid_emails),
        "unpaid_members": unpaid_members,
        "approved_count": len(approved_rows),
        "pending_count": len(pending_rows),
        "rejected_count": len(rejected_rows),
        "contributions": month_rows,
    }


@router.get("/yearly")
def yearly_report(
    year: str | None = None,
    current_user=Depends(get_current_user),
):
    report_year = year or str(datetime.utcnow().year)

    contributions = read_sheet_rows("Contributions")

    if current_user.role != "admin":
        contributions = [
            row
            for row in contributions
            if _contribution_email(row) == current_user.email.lower()
        ]

    year_rows = [
        row
        for row in contributions
        if _contribution_month(row).startswith(f"{report_year}-")
        or _text(row.get("Year")) == report_year
    ]

    monthly = []

    for month_number in range(1, 13):
        month_key = f"{report_year}-{month_number:02d}"

        month_rows = [
            row
            for row in year_rows
            if _contribution_month(row) == month_key
        ]

        approved_amount = sum(
            _amount(row.get("Amount"))
            for row in month_rows
            if _contribution_status(row) == "approved"
        )

        pending_amount = sum(
            _amount(row.get("Amount"))
            for row in month_rows
            if _contribution_status(row) == "pending"
        )

        monthly.append(
            {
                "month": month_key,
                "approved_amount": approved_amount,
                "pending_amount": pending_amount,
            }
        )

    return {
        "year": report_year,
        "total_approved": sum(item["approved_amount"] for item in monthly),
        "total_pending": sum(item["pending_amount"] for item in monthly),
        "monthly": monthly,
    }