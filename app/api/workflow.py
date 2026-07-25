"""
Endpoint to trigger a new workflow run.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_role
from app.services.workflow_service import WorkflowService

class WorkflowStartRequest(BaseModel):
    intent: str  # e.g., "I want to book an appointment with a cardiologist"

router = APIRouter()

@router.post("/start")
def start_workflow(
    request: WorkflowStartRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("patient"))
):
    service = WorkflowService(db)
    final_state = service.start_workflow(
        patient_user_id=current_user.id,
        intent=request.intent,
    )
    return {"workflow_status": "completed", "final_state": final_state}