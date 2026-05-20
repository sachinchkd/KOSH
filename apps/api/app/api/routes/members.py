from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.contribution import Contribution
from app.models.user import User
from app.schemas.members import MemberCreate, MemberOut, MemberUpdate
from app.services.audit import write_audit

router = APIRouter(prefix="/members", tags=["members"])


def _member_out(db: Session, user: User) -> MemberOut:
    total_paid = (
        db.query(func.coalesce(func.sum(Contribution.amount), 0))
        .filter(Contribution.member_id == user.id, Contribution.status == "approved")
        .scalar()
    )
    return MemberOut(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        joined_at=user.joined_at,
        is_active=user.is_active,
        total_paid=int(total_paid or 0),
    )


@router.get("", response_model=list[MemberOut])
def list_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    users = db.query(User).order_by(User.role, User.name).all()
    return [_member_out(db, user) for user in users]


@router.post("", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def create_member(
    payload: MemberCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    if payload.role not in {"admin", "member"}:
        raise HTTPException(status_code=400, detail="Role must be admin or member")

    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        role=payload.role,
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.flush()
    write_audit(db, "member.created", admin, "user", user.id, {"email": user.email})
    db.commit()
    db.refresh(user)
    return _member_out(db, user)


@router.patch("/{member_id}", response_model=MemberOut)
def update_member(
    member_id: int,
    payload: MemberUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.get(User, member_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Member not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    write_audit(db, "member.updated", admin, "user", user.id, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(user)
    return _member_out(db, user)
