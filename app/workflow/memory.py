"""
SQLite-backed LangGraph checkpointer using the existing WorkflowRun model.
"""
from typing import Optional, Dict, Any, Iterator, List, Tuple
from langgraph.checkpoint.base import BaseCheckpointSaver, CheckpointTuple
from langchain_core.runnables import RunnableConfig
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.workflow import WorkflowRun
import json

class WorkflowCheckpointer(BaseCheckpointSaver):
    """
    Persists LangGraph checkpoints in the workflow_runs table (state_snapshot column).
    thread_id is mapped to WorkflowRun.id.
    """

    def get(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return None

        db: Session = SessionLocal()
        try:
            run = db.query(WorkflowRun).filter(WorkflowRun.id == thread_id).first()
            if not run or not run.state_snapshot:
                return None
            state = json.loads(run.state_snapshot)
            # The checkpoint must contain at least {"v":..., "id":..., "ts":..., "channel_values": {...}}
            # We store the whole state as channel_values and add minimal metadata.
            checkpoint = {
                "v": 1,
                "id": run.id,
                "ts": run.updated_at.isoformat(),
                "channel_values": state,
            }
            # We need to return a CheckpointTuple with config and checkpoint
            return CheckpointTuple(
                config=config,
                checkpoint=checkpoint,
                metadata={},
                parent_config=None,
            )
        finally:
            db.close()

    def put(self, config: RunnableConfig, checkpoint: Dict[str, Any], metadata: Dict[str, Any]) -> RunnableConfig:
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return config

        db: Session = SessionLocal()
        try:
            run = db.query(WorkflowRun).filter(WorkflowRun.id == thread_id).first()
            if run:
                run.state_snapshot = json.dumps(checkpoint.get("channel_values", {}))
                run.current_step = checkpoint.get("channel_values", {}).get("current_step")
                run.status = "running"
                db.commit()
        finally:
            db.close()
        return config

    def put_writes(self, config: RunnableConfig, writes: List[Tuple[str, Any]], task_id: str) -> RunnableConfig:
        # Not strictly needed for basic persistence but required by interface
        return config