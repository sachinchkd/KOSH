import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


def write_audit(
    db: Session,
    action: str,
    performed_by: User | None,
    target_type: str | None = None,
    target_id: str | int | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    db.add(
        AuditLog(
            action=action,
            performed_by_id=performed_by.id if performed_by else None,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            metadata_json=json.dumps(metadata or {}),
        )
    )
