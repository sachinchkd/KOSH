from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.deps import get_current_user, require_admin
from app.services.google import append_sheet_row, read_sheet_rows, update_sheet_row, upload_file_to_drive
from app.services.storage import save_upload

router = APIRouter(prefix="/contributions", tags=["contributions"])


def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def _text(value) -> str:
    return str(value or "").strip()


def _lower(value) -> str:
    return _text(value).lower()


def _amount(value) -> int:
    try:
        return int(float(_text(value).replace(",", "")))
    except ValueError:
        return 0


def _member_row(data: dict) -> list:
    return [
        data.get("Member ID", ""),
        data.get("Name", ""),
        data.get("Email", ""),
        data.get("Phone", ""),
        data.get("Role", "member"),
        data.get("Joined Date", ""),
        data.get("Status", "Active"),
        data.get("Total Paid", "0"),
    ]


def _contribution_row(data: dict) -> list:
    return [
        data.get("ID", ""),
        data.get("Member Name", ""),
        data.get("Month", ""),
        data.get("Amount", "0"),
        data.get("Payment", data.get(" Payment", "")),
        data.get("Status", "Pending"),
        data.get("URL", ""),
        data.get("Submitted_At", ""),
        data.get("Approved_At", ""),
        data.get("Approved_By", ""),
        data.get("Remarks", ""),
    ]


def _row_to_out(row: dict) -> dict:
    payment = row.get("Payment") or row.get(" Payment") or ""

    return {
        "id": _text(row.get("ID")),
        "member_name": _text(row.get("Member Name")),
        "month": _text(row.get("Month")),
        "amount": _amount(row.get("Amount")),
        "payment": _text(payment),
        "payment_method": _text(payment),
        "status": _text(row.get("Status")) or "Pending",
        "url": _text(row.get("URL")),
        "photo_url": _text(row.get("URL")),
        "submitted_at": _text(row.get("Submitted_At")),
        "approved_at": _text(row.get("Approved_At")),
        "approved_by": _text(row.get("Approved_By")),
        "remarks": _text(row.get("Remarks")),
    }


def _find_current_member(current_user):
    members = read_sheet_rows("Members")

    for member in members:
        if _lower(member.get("Email")) == current_user.email.lower():
            return member

    return {
        "Member ID": current_user.email,
        "Name": current_user.name or current_user.email,
        "Email": current_user.email,
        "Phone": "",
        "Role": current_user.role,
        "Joined Date": "",
        "Status": "Active",
        "Total Paid": "0",
    }


def _find_member_for_submission(member_id: Optional[str], current_user):
    members = read_sheet_rows("Members")

    if member_id:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Only admins can submit for another member",
            )

        for member in members:
            if _text(member.get("Member ID")) == member_id:
                return member

        raise HTTPException(status_code=404, detail="Member not found")

    return _find_current_member(current_user)


def _update_member_total(member_name: str, amount_change: int):
    members = read_sheet_rows("Members")

    for member in members:
        if _lower(member.get("Name")) == _lower(member_name):
            current_total = _amount(member.get("Total Paid"))
            new_total = max(0, current_total + amount_change)

            member["Total Paid"] = str(new_total)

            update_sheet_row(
                "Members",
                int(member["_row_number"]),
                _member_row(member),
            )
            return


@router.get("")
def list_contributions(
    status_filter: Optional[str] = None,
    month: Optional[str] = None,
    current_user=Depends(get_current_user),
):
    rows = read_sheet_rows("Contributions")

    if current_user.role != "admin":
        current_member = _find_current_member(current_user)
        current_member_name = _lower(current_member.get("Name"))

        rows = [
            row for row in rows
            if _lower(row.get("Member Name")) == current_member_name
        ]

    if status_filter:
        rows = [
            row for row in rows
            if _lower(row.get("Status")) == status_filter.lower()
        ]

    if month:
        rows = [
            row for row in rows
            if _text(row.get("Month")) == month
        ]

    return [_row_to_out(row) for row in reversed(rows)]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_contribution(
    month: str = Form(...),
    amount: int = Form(default=1000),
    payment: Optional[str] = Form(default=None),
    payment_method: Optional[str] = Form(default=None),
    member_id: Optional[str] = Form(default=None),
    remarks: Optional[str] = Form(default=None),
    photo: Optional[UploadFile] = File(default=None),
    current_user=Depends(get_current_user),
):
    member = _find_member_for_submission(member_id, current_user)

    final_payment = payment or payment_method
    if not final_payment:
        raise HTTPException(status_code=400, detail="Payment is required")

    url = ""

    if photo is not None:
        stored = await save_upload(photo)
        url = upload_file_to_drive(
            str(stored.path),
            stored.filename,
            photo.content_type,
        )

    data = {
        "ID": str(uuid4()),
        "Member Name": _text(member.get("Name")),
        "Month": month,
        "Amount": str(amount),
        "Payment": final_payment,
        "Status": "Pending",
        "URL": url,
        "Submitted_At": _now(),
        "Approved_At": "",
        "Approved_By": "",
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
        if _text(row.get("ID")) == contribution_id:
            old_status = _lower(row.get("Status"))

            row["Status"] = "Approved"
            row["Approved_At"] = _now()
            row["Approved_By"] = admin.email

            update_sheet_row(
                "Contributions",
                int(row["_row_number"]),
                _contribution_row(row),
            )

            if old_status != "approved":
                _update_member_total(
                    member_name=_text(row.get("Member Name")),
                    amount_change=_amount(row.get("Amount")),
                )

            return _row_to_out(row)

    raise HTTPException(status_code=404, detail="Contribution not found")


@router.patch("/{contribution_id}/reject")
def reject_contribution(
    contribution_id: str,
    payload: dict,
    admin=Depends(require_admin),
):
    rows = read_sheet_rows("Contributions")

    for row in rows:
        if _text(row.get("ID")) == contribution_id:
            old_status = _lower(row.get("Status"))

            row["Status"] = "Rejected"
            row["Approved_At"] = ""
            row["Approved_By"] = ""

            rejection_remarks = _text(payload.get("remarks"))
            if rejection_remarks:
                row["Remarks"] = rejection_remarks

            update_sheet_row(
                "Contributions",
                int(row["_row_number"]),
                _contribution_row(row),
            )

            if old_status == "approved":
                _update_member_total(
                    member_name=_text(row.get("Member Name")),
                    amount_change=-_amount(row.get("Amount")),
                )

            return _row_to_out(row)

    raise HTTPException(status_code=404, detail="Contribution not found")