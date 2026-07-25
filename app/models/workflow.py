"""
Tracks multi-agent workflow execution per patient request.
"""
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class WorkflowRun(BaseModel):
    __tablename__ = "workflow_runs"

    patient_id: Mapped[str] = mapped_column(ForeignKey("patient_profiles.id"))
    intent: Mapped[str] = mapped_column(String(200), nullable=True)
    current_step: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, running, completed, failed
    state_snapshot: Mapped[str] = mapped_column(Text, nullable=True)  # JSON snapshot of LangGraph state
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    patient: Mapped["PatientProfile"] = relationship(back_populates="workflow_runs")