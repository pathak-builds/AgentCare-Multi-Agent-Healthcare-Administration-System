from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import require_role
from app.repositories.audit_repository import AuditRepository
from app.schemas.audit import AuditEventOut
from typing import List

router = APIRouter()

@router.get("/audit", response_model=List[AuditEventOut])
def audit_logs(
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    repo = AuditRepository(db)
    return repo.get_all(limit)