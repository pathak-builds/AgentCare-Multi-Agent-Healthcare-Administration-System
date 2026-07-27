"""
Service to create and manage workflow runs.
"""

import json
import traceback
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
)

from app.models.workflow import WorkflowRun
from app.repositories.patient_repository import PatientRepository
from app.workflow.graph import build_workflow
from app.workflow.state import AgentCareState
from app.utils.audit import log_audit_event


class WorkflowService:
    def __init__(self, db: Session):
        self.db = db
        self.patient_repo = PatientRepository(db)

    def _serialize_state(self, state: dict) -> dict:
        """
        Convert LangGraph state into a JSON-serializable dictionary.
        """

        serialized = {}

        for key, value in state.items():

            if key == "messages":

                serialized["messages"] = []

                for msg in value:

                    serialized["messages"].append(
                        {
                            "type": msg.__class__.__name__,
                            "content": getattr(msg, "content", ""),
                        }
                    )

            else:
                try:
                    json.dumps(value)
                    serialized[key] = value

                except TypeError:
                    serialized[key] = str(value)

        return serialized

    def start_workflow(
        self,
        patient_user_id: str,
        intent: str,
    ) -> dict:
        """
        Create a workflow run, execute the LangGraph workflow,
        persist its final state, and return the final state.
        """

        # ---------------------------------------------------
        # Ensure patient exists
        # ---------------------------------------------------

        patient = self.patient_repo.get_by_user_id(patient_user_id)

        if not patient:
            raise HTTPException(
                status_code=400,
                detail="Patient profile not found",
            )

        # ---------------------------------------------------
        # Create workflow run
        # ---------------------------------------------------

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

        # ---------------------------------------------------
        # Build workflow
        # ---------------------------------------------------

        graph = build_workflow()

        initial_state: AgentCareState = {
            "messages": [
                HumanMessage(content=intent)
            ],
            "patient_id": patient.id,
            "intent": intent,
            "current_step": "coordinator",
            "agent_outputs": {},
            "error": None,
            "thread_id": run.id,
        }

        config = {
            "configurable": {
                "thread_id": run.id,
            }
        }

        # ---------------------------------------------------
        # Execute workflow
        # ---------------------------------------------------

        try:

            final_state = graph.invoke(
                initial_state,
                config,
            )

        except Exception as e:

            traceback.print_exc()

            run.status = "failed"
            run.error_message = str(e)
            run.current_step = initial_state.get(
                "current_step",
                "failed",
            )

            serialized_state = self._serialize_state(initial_state)

            run.state_snapshot = json.dumps(
                serialized_state,
                indent=2,
            )

            self.db.commit()

            log_audit_event(
                self.db,
                patient_user_id,
                "workflow_failed",
                f"Workflow {run.id} failed: {e}",
            )

            raise HTTPException(
                status_code=500,
                detail=f"Workflow execution failed: {e}",
            )

        # ---------------------------------------------------
        # Save final state
        # ---------------------------------------------------

        serialized_state = self._serialize_state(final_state)

        run.status = "completed"
        run.current_step = final_state.get(
            "current_step",
            "completed",
        )

        run.state_snapshot = json.dumps(
            serialized_state,
            indent=2,
        )

        run.error_message = final_state.get("error")

        self.db.commit()

        log_audit_event(
            self.db,
            patient_user_id,
            "workflow_completed",
            f"Workflow {run.id} completed with intent '{intent}'",
        )

        return final_state