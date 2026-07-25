"""
Doctor entity, linked to a user (role=staff) and a department.
"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class Doctor(BaseModel):
    __tablename__ = "doctors"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.id"))
    specialization: Mapped[str] = mapped_column(String(200), nullable=True)
    license_number: Mapped[str] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship(back_populates="doctor")
    department: Mapped["Department"] = relationship(back_populates="doctors")
    appointment_slots: Mapped[list["AppointmentSlot"]] = relationship(back_populates="doctor")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="doctor")