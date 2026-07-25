"""
Utility to log audit events across services.
"""
from sqlalchemy.orm import Session
from app.models.audit import AuditEvent

def log_audit_event(
    db: Session,
    user_id: str | None,
    event_type: str,
    description: str,
    ip_address: str | None = None
):
    event = AuditEvent(
        user_id=user_id,
        event_type=event_type,
        description=description,
        ip_address=ip_address,
    )
    db.add(event)
    db.commit()