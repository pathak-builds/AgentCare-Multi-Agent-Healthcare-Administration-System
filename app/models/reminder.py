"""
Reminders linked to appointments or follow-ups.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .appointment import Appointment

class Reminder(BaseModel):
    __tablename__ = "reminders"

    appointment_id: Mapped[str] = mapped_column(ForeignKey("appointments.id"), unique=True)
    reminder_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    message: Mapped[str] = mapped_column(String(500))
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    appointment: Mapped["Appointment"] = relationship(back_populates="reminder")