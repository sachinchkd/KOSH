from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user, require_admin
from app.services.google import append_sheet_row, read_sheet_rows, update_sheet_row

router = APIRouter(prefix="/members", tags=["members"])


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


def _row_to_member(row: dict) -> dict:
    return {
        "id": _text(row.get("Member ID")),
        "name": _text(row.get("Name")),
        "email": _text(row.get("Email")),
        "phone": _text(row.get("Phone")),
        "role": _lower(row.get("Role")) or "member",
        "joined_at": _text(row.get("Joined Date")),
        "is_active": _lower(row.get("Status", "Active")) in {"active", "true", "yes", "1"},
        "total_paid": _amount(row.get("Total Paid")),
    }


def _current_user_as_member(current_user) -> dict:
    return {
        "id": current_user.email,
        "name": current_user.name or current_user.email,
        "email": current_user.email,
        "phone": "",
        "role": current_user.role,
        "joined_at": "",
        "is_active": True,
        "total_paid": 0,
    }


@router.get("")
def list_members(current_user=Depends(get_current_user)):
    rows = read_sheet_rows("Members")

    if current_user.role == "admin":
        return [_row_to_member(row) for row in rows]

    for row in rows:
        if _lower(row.get("Email")) == current_user.email.lower():
            return [_row_to_member(row)]

    return [_current_user_as_member(current_user)]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_member(payload: dict, admin=Depends(require_admin)):
    rows = read_sheet_rows("Members")

    email = _lower(payload.get("email"))
    name = _text(payload.get("name"))
    phone = _text(payload.get("phone"))
    role = _lower(payload.get("role")) or "member"

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    if not name:
        name = email

    if role not in {"admin", "member"}:
        raise HTTPException(status_code=400, detail="Role must be admin or member")

    for row in rows:
        if _lower(row.get("Email")) == email:
            raise HTTPException(status_code=400, detail="Member already exists")

    data = {
        "Member ID": str(uuid4()),
        "Name": name,
        "Email": email,
        "Phone": phone,
        "Role": role,
        "Joined Date": datetime.utcnow().strftime("%Y-%m-%d"),
        "Status": "Active",
        "Total Paid": "0",
    }

    append_sheet_row("Members", _member_row(data))

    return _row_to_member(data)


@router.get("/{member_id}")
def get_member(member_id: str, current_user=Depends(get_current_user)):
    rows = read_sheet_rows("Members")

    for row in rows:
        if _text(row.get("Member ID")) == member_id:
            if (
                current_user.role != "admin"
                and _lower(row.get("Email")) != current_user.email.lower()
            ):
                raise HTTPException(status_code=403, detail="Not allowed")

            return _row_to_member(row)

    if member_id == current_user.email:
        return _current_user_as_member(current_user)

    raise HTTPException(status_code=404, detail="Member not found")


@router.patch("/{member_id}")
def update_member(member_id: str, payload: dict, admin=Depends(require_admin)):
    rows = read_sheet_rows("Members")

    for row in rows:
        if _text(row.get("Member ID")) == member_id:
            if "name" in payload:
                row["Name"] = _text(payload.get("name"))

            if "email" in payload:
                email = _lower(payload.get("email"))
                if not email:
                    raise HTTPException(status_code=400, detail="Email is required")
                row["Email"] = email

            if "phone" in payload:
                row["Phone"] = _text(payload.get("phone"))

            if "role" in payload:
                role = _lower(payload.get("role"))
                if role not in {"admin", "member"}:
                    raise HTTPException(status_code=400, detail="Role must be admin or member")
                row["Role"] = role

            if "status" in payload:
                row["Status"] = _text(payload.get("status")) or "Active"

            update_sheet_row("Members", int(row["_row_number"]), _member_row(row))
            return _row_to_member(row)

    raise HTTPException(status_code=404, detail="Member not found")


@router.delete("/{member_id}")
def deactivate_member(member_id: str, admin=Depends(require_admin)):
    rows = read_sheet_rows("Members")

    for row in rows:
        if _text(row.get("Member ID")) == member_id:
            row["Status"] = "Inactive"
            update_sheet_row("Members", int(row["_row_number"]), _member_row(row))
            return {"ok": True, "message": "Member deactivated"}

    raise HTTPException(status_code=404, detail="Member not found")