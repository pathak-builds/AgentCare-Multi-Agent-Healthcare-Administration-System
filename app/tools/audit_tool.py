"""
Tool to create an audit event.
"""
from langchain_core.tools import tool
from app.database.session import SessionLocal
from app.utils.audit import log_audit_event

@tool
def audit_log(event_type: str, description: str) -> str:
    """Log an audit event. Provide event_type and description. Returns 'Audit logged'."""
    db = SessionLocal()
    try:
        log_audit_event(db, user_id=None, event_type=event_type, description=description)
        return "Audit event logged successfully."
    finally:
        db.close()