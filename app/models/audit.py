"""
Immutable audit log for all significant actions.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .user import User

class AuditEvent(BaseModel):
    __tablename__ = "audit_events"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100))  # e.g., "patient_registered", "appointment_booked"
    description: Mapped[str] = mapped_column(Text)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)

    user: Mapped["User"] = relationship(back_populates="audit_events")