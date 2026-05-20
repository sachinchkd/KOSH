from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.contribution import Contribution
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly")
def monthly_report(
    month: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Contribution).filter(Contribution.month == month)
    if current_user.role != "admin":
        query = query.filter(Contribution.member_id == current_user.id)

    approved = query.with_entities(func.coalesce(func.sum(Contribution.amount), 0)).filter(Contribution.status == "approved").scalar()
    pending = query.with_entities(func.coalesce(func.sum(Contribution.amount), 0)).filter(Contribution.status == "pending").scalar()
    rejected = query.with_entities(func.coalesce(func.sum(Contribution.amount), 0)).filter(Contribution.status == "rejected").scalar()

    rows = []
    for item in query.order_by(Contribution.submitted_at.desc()).all():
        rows.append({
            "id": item.id,
            "member_name": item.member.name,
            "amount": item.amount,
            "payment_method": item.payment_method,
            "status": item.status,
            "submitted_at": item.submitted_at,
            "photo_url": item.photo_url,
            "remarks": item.remarks,
        })

    return {
        "month": month,
        "approved": int(approved or 0),
        "pending": int(pending or 0),
        "rejected": int(rejected or 0),
        "rows": rows,
    }
