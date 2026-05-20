from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin
from app.core.config import get_settings
from app.db.session import get_db
from app.models.contribution import Contribution
from app.models.user import User
from app.schemas.contributions import ContributionOut, ContributionStatusUpdate
from app.services.audit import write_audit
from app.services.google import append_contribution_to_sheet, upload_file_to_drive
from app.services.storage import save_upload

settings = get_settings()
router = APIRouter(prefix="/contributions", tags=["contributions"])


def _out(contribution: Contribution) -> ContributionOut:
    return ContributionOut(
        id=contribution.id,
        member_id=contribution.member_id,
        member_name=contribution.member.name,
        month=contribution.month,
        amount=contribution.amount,
        payment_method=contribution.payment_method,
        status=contribution.status,
        photo_url=contribution.photo_url,
        remarks=contribution.remarks,
        submitted_at=contribution.submitted_at,
        approved_at=contribution.approved_at,
        approved_by_name=contribution.approved_by.name if contribution.approved_by else None,
        google_sheet_row_id=contribution.google_sheet_row_id,
    )


@router.get("", response_model=list[ContributionOut])
def list_contributions(
    status_filter: str | None = None,
    month: str | None = None,
    member_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Contribution)

    if current_user.role != "admin":
        query = query.filter(Contribution.member_id == current_user.id)
    elif member_id is not None:
        query = query.filter(Contribution.member_id == member_id)

    if status_filter:
        query = query.filter(Contribution.status == status_filter)
    if month:
        query = query.filter(Contribution.month == month)

    contributions = query.order_by(Contribution.submitted_at.desc()).all()
    return [_out(item) for item in contributions]


@router.post("", response_model=ContributionOut, status_code=status.HTTP_201_CREATED)
async def create_contribution(
    member_id: int | None = Form(default=None),
    month: str = Form(...),
    amount: int = Form(default=1000),
    payment_method: str = Form(default="Cash"),
    remarks: str | None = Form(default=None),
    photo: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if len(month) != 7 or month[4] != "-":
        raise HTTPException(status_code=400, detail="Month must use YYYY-MM format")

    target_member_id = member_id if current_user.role == "admin" and member_id else current_user.id
    member = db.get(User, target_member_id)
    if member is None or not member.is_active:
        raise HTTPException(status_code=404, detail="Member not found")

    existing = (
        db.query(Contribution)
        .filter(Contribution.member_id == target_member_id, Contribution.month == month, Contribution.status != "rejected")
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="A non-rejected contribution already exists for this member and month")

    photo_url = None
    if photo is not None:
        stored = await save_upload(photo)
        photo_url = stored.public_url
        try:
            drive_url = upload_file_to_drive(stored.path, stored.filename, photo.content_type)
            if drive_url:
                photo_url = drive_url
        except Exception:
            # Local upload still works even if Google Drive is not configured correctly.
            photo_url = stored.public_url

    contribution = Contribution(
        member_id=target_member_id,
        month=month,
        amount=amount,
        payment_method=payment_method,
        photo_url=photo_url,
        remarks=remarks,
        status="pending",
    )
    db.add(contribution)
    db.flush()
    write_audit(db, "contribution.created", current_user, "contribution", contribution.id)

    try:
        row_id = append_contribution_to_sheet(contribution, member)
        contribution.google_sheet_row_id = row_id
    except Exception:
        contribution.google_sheet_row_id = None

    db.commit()
    db.refresh(contribution)
    return _out(contribution)


@router.patch("/{contribution_id}/approve", response_model=ContributionOut)
def approve_contribution(
    contribution_id: int,
    payload: ContributionStatusUpdate | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    contribution = db.get(Contribution, contribution_id)
    if contribution is None:
        raise HTTPException(status_code=404, detail="Contribution not found")

    contribution.status = "approved"
    contribution.approved_at = datetime.utcnow()
    contribution.approved_by_id = admin.id
    if payload and payload.remarks:
        contribution.remarks = payload.remarks

    write_audit(db, "contribution.approved", admin, "contribution", contribution.id)
    db.commit()
    db.refresh(contribution)
    return _out(contribution)


@router.patch("/{contribution_id}/reject", response_model=ContributionOut)
def reject_contribution(
    contribution_id: int,
    payload: ContributionStatusUpdate | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    contribution = db.get(Contribution, contribution_id)
    if contribution is None:
        raise HTTPException(status_code=404, detail="Contribution not found")

    contribution.status = "rejected"
    contribution.approved_at = None
    contribution.approved_by_id = None
    if payload and payload.remarks:
        contribution.remarks = payload.remarks

    write_audit(db, "contribution.rejected", admin, "contribution", contribution.id)
    db.commit()
    db.refresh(contribution)
    return _out(contribution)
