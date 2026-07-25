"""
Escalations that require human approval (e.g., safety blocks, complex requests).
"""
from __future__ import annotations

from typing import TYPE_CHECKING
import enum

from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .workflow import WorkflowRun
    from .user import User

class EscalationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Escalation(BaseModel):
    __tablename__ = "escalations"

    workflow_run_id: Mapped[str] = mapped_column(ForeignKey("workflow_runs.id"), nullable=True)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[EscalationStatus] = mapped_column(SQLEnum(EscalationStatus), default=EscalationStatus.PENDING)
    reviewer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True)
    decision_notes: Mapped[str] = mapped_column(Text, nullable=True)

    workflow_run: Mapped["WorkflowRun"] = relationship(backref="escalations")
    reviewer: Mapped["User"] = relationship(foreign_keys=[reviewer_id])