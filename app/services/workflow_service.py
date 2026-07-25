"""
Service to create and manage workflow runs.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.workflow import WorkflowRun
from app.repositories.patient_repository import PatientRepository
from app.workflow.graph import build_workflow
from app.workflow.state import AgentCareState
from app.utils.audit import log_audit_event
import uuid
import traceback


class WorkflowService:
    def __init__(self, db: Session):
        self.db = db
        self.patient_repo = PatientRepository(db)

    def start_workflow(self, patient_user_id: str, intent: str) -> dict:
        """Create a new workflow run, execute the graph, and return the final state."""
        # Ensure patient profile exists
        patient = self.patient_repo.get_by_user_id(patient_user_id)
        if not patient:
            raise HTTPException(status_code=400, detail="Patient profile not found")

        # Create WorkflowRun record
        run = WorkflowRun(
            id=str(uuid.uuid4()),
            patient_id=patient.id,
            intent=intent,
            current_step="coordinator",
            status="pending",
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        # Build the compiled graph
        graph = build_workflow()

        # Initial state
        initial_state: AgentCareState = {
            "messages": [],
            "patient_id": patient.id,
            "intent": intent,
            "current_step": "coordinator",
            "agent_outputs": {},
            "error": None,
        }

        # Configuration with thread_id = run.id for persistence
        config = {"configurable": {"thread_id": run.id}}

        try:
            # Invoke the graph (will run all nodes synchronously)
            final_state = graph.invoke(initial_state, config)
        except Exception as e:
            traceback.print_exc()
            # Update run with error
            run.status = "failed"
            run.error_message = str(e)
            run.state_snapshot = str(initial_state)
            self.db.commit()
            log_audit_event(self.db, patient_user_id, "workflow_failed", f"Workflow {run.id} failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

        # Update run with final state
        run.status = "completed"
        run.current_step = final_state.get("current_step", "completed")
        run.state_snapshot = str(final_state)  # could be JSON serialized, but str is fine for placeholder
        self.db.commit()

        log_audit_event(self.db, patient_user_id, "workflow_completed", f"Workflow {run.id} completed with intent '{intent}'")

        return final_state