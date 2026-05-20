from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.deps import get_current_user, require_admin
from app.services.google import append_sheet_row, read_sheet_rows, update_sheet_row, upload_file_to_drive
from app.services.storage import save_upload

router = APIRouter(prefix="/contributions", tags=["contributions"])


CONTRIBUTION_HEADERS = [
    "ID",
    "Member Email",
    "Member Name",
    "Month",
    "Year",
    "Amount",
    "Payment Method",
    "Status",
    "Photo URL",
    "Browser Date",
    "Submitted At",
    "Approved At",
    "Approved By",
    "Remarks",
]


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _normalize(value: str | None) -> str:
    return str(value or "").strip()


def _row_to_out(row: dict) -> dict:
    return {
        "id": row.get("ID", ""),
        "member_email": row.get("Member Email", ""),
        "member_name": row.get("Member Name", ""),
        "month": row.get("Month", ""),
        "year": row.get("Year", ""),
        "amount": int(row.get("Amount") or 0),
        "payment_method": row.get("Payment Method", ""),
        "status": row.get("Status", ""),
        "photo_url": row.get("Photo URL", ""),
        "browser_date": row.get("Browser Date", ""),
        "submitted_at": row.get("Submitted At", ""),
        "approved_at": row.get("Approved At", ""),
        "approved_by": row.get("Approved By", ""),
        "remarks": row.get("Remarks", ""),
    }


def _contribution_row(data: dict) -> list:
    return [
        data.get("ID", ""),
        data.get("Member Email", ""),
        data.get("Member Name", ""),
        data.get("Month", ""),
        data.get("Year", ""),
        data.get("Amount", ""),
        data.get("Payment Method", ""),
        data.get("Status", ""),
        data.get("Photo URL", ""),
        data.get("Browser Date", ""),
        data.get("Submitted At", ""),
        data.get("Approved At", ""),
        data.get("Approved By", ""),
        data.get("Remarks", ""),
    ]


@router.get("")
def list_contributions(
    status_filter: str | None = None,
    month: str | None = None,
    current_user=Depends(get_current_user),
):
    rows = read_sheet_rows("Contributions")

    if current_user.role != "admin":
        rows = [
            row for row in rows
            if _normalize(row.get("Member Email")).lower() == current_user.email.lower()
        ]

    if status_filter:
        rows = [
            row for row in rows
            if _normalize(row.get("Status")).lower() == status_filter.lower()
        ]

    if month:
        rows = [
            row for row in rows
            if _normalize(row.get("Month")) == month
        ]

    return [_row_to_out(row) for row in reversed(rows)]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_contribution(
    month: str = Form(...),
    year: str = Form(...),
    browser_date: str = Form(...),
    amount: int = Form(default=1000),
    payment_method: str = Form(default="Online"),
    remarks: str | None = Form(default=None),
    photo: UploadFile | None = File(default=None),
    current_user=Depends(get_current_user),
):
    photo_url = ""

    if photo is not None:
        stored = await save_upload(photo)
        photo_url = upload_file_to_drive(
            str(stored.path),
            stored.filename,
            photo.content_type,
        )

    contribution_id = str(uuid4())

    data = {
        "ID": contribution_id,
        "Member Email": current_user.email,
        "Member Name": current_user.name or current_user.email,
        "Month": month,
        "Year": year,
        "Amount": amount,
        "Payment Method": payment_method,
        "Status": "Pending",
        "Photo URL": photo_url,
        "Browser Date": browser_date,
        "Submitted At": _now(),
        "Approved At": "",
        "Approved By": "",
        "Remarks": remarks or "",
    }

    append_sheet_row("Contributions", _contribution_row(data))

    return _row_to_out(data)


@router.patch("/{contribution_id}/approve")
def approve_contribution(
    contribution_id: str,
    admin=Depends(require_admin),
):
    rows = read_sheet_rows("Contributions")

    for row in rows:
        if row.get("ID") == contribution_id:
            row["Status"] = "Approved"
            row["Approved At"] = _now()
            row["Approved By"] = admin.email

            update_sheet_row(
                "Contributions",
                row["_row_number"],
                _contribution_row(row),
            )

            return _row_to_out(row)

    raise HTTPException(status_code=404, detail="Contribution not found")


@router.patch("/{contribution_id}/reject")
def reject_contribution(
    contribution_id: str,
    remarks: str | None = None,
    admin=Depends(require_admin),
):
    rows = read_sheet_rows("Contributions")

    for row in rows:
        if row.get("ID") == contribution_id:
            row["Status"] = "Rejected"
            row["Approved At"] = _now()
            row["Approved By"] = admin.email

            if remarks:
                row["Remarks"] = remarks

            update_sheet_row(
                "Contributions",
                row["_row_number"],
                _contribution_row(row),
            )

            return _row_to_out(row)

    raise HTTPException(status_code=404, detail="Contribution not found")