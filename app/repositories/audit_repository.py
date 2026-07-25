from sqlalchemy.orm import Session
from app.models.audit import AuditEvent

class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, event: AuditEvent) -> AuditEvent:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_all(self, limit: int = 100) -> list[AuditEvent]:
        return self.db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit).all()