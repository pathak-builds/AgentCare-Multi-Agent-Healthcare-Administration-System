"""
Appointment booking linking patient, doctor, and slot.
"""
from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel
import enum

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    RESCHEDULED = "rescheduled"

class Appointment(BaseModel):
    __tablename__ = "appointments"

    patient_id: Mapped[str] = mapped_column(ForeignKey("patient_profiles.id"))
    doctor_id: Mapped[str] = mapped_column(ForeignKey("doctors.id"))
    slot_id: Mapped[str] = mapped_column(ForeignKey("appointment_slots.id"), unique=True)
    status: Mapped[AppointmentStatus] = mapped_column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    reason: Mapped[str] = mapped_column(String(500), nullable=True)
    notes: Mapped[str] = mapped_column(String(1000), nullable=True)

    patient: Mapped["PatientProfile"] = relationship(back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship(back_populates="appointments")
    slot: Mapped["AppointmentSlot"] = relationship(back_populates="appointment")
    reminder: Mapped["Reminder"] = relationship(back_populates="appointment", uselist=False)