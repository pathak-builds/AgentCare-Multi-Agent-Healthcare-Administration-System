"""
Available appointment slots for a doctor.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .doctor import Doctor
    from .department import Department
    from .appointment import Appointment

class AppointmentSlot(BaseModel):
    __tablename__ = "appointment_slots"

    doctor_id: Mapped[str] = mapped_column(ForeignKey("doctors.id"))
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.id"))
    start_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    is_booked: Mapped[bool] = mapped_column(Boolean, default=False)

    doctor: Mapped["Doctor"] = relationship(back_populates="appointment_slots")
    department: Mapped["Department"] = relationship(back_populates="appointment_slots")
    appointment: Mapped["Appointment"] = relationship(back_populates="slot", uselist=False)