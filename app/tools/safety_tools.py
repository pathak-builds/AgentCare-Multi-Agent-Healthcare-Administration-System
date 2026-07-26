"""
Tools for the Safety Agent: escalation creation and safety audit logging.
"""

import json

from langchain_core.tools import tool

from app.database.session import SessionLocal
from app.models.escalation import Escalation
from app.utils.audit import log_audit_event


@tool
def create_escalation(workflow_run_id: str, reason: str) -> str:
    """
    Create a pending escalation for human review.
    """

    db = SessionLocal()

    try:

        escalation = Escalation(
            workflow_run_id=workflow_run_id,
            reason=reason,
            status="pending",
        )

        db.add(escalation)
        db.commit()
        db.refresh(escalation)

        return json.dumps({
            "status": "success",
            "escalation_id": str(escalation.id),
            "workflow_run_id": workflow_run_id,
            "message": "Escalation created successfully."
        })

    except Exception as e:

        db.rollback()

        return json.dumps({
            "status": "failure",
            "message": str(e)
        })

    finally:

        db.close()


@tool
def log_safety_audit(workflow_run_id: str, description: str) -> str:
    """
    Record a safety-related audit event.
    """

    db = SessionLocal()

    try:

        log_audit_event(
            db=db,
            user_id=None,
            event_type="safety_check",
            description=f"Workflow {workflow_run_id}: {description}",
        )

        return json.dumps({
            "status": "success",
            "message": "Safety audit logged."
        })

    except Exception as e:

        db.rollback()

        return json.dumps({
            "status": "failure",
            "message": str(e)
        })

    finally:

        db.close()