"""
Patient profile linked to a user (role=patient).
"""
from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class PatientProfile(BaseModel):
    __tablename__ = "patient_profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    date_of_birth: Mapped[Date] = mapped_column(Date, nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    emergency_contact: Mapped[str] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship(back_populates="patient_profile")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="patient")
    documents: Mapped[list["PatientDocument"]] = relationship(back_populates="patient")
    workflow_runs: Mapped[list["WorkflowRun"]] = relationship(back_populates="patient")