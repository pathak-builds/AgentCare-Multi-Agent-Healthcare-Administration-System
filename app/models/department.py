"""
Hospital department entity.
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class Department(BaseModel):
    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    doctors: Mapped[list["Doctor"]] = relationship(back_populates="department")
    appointment_slots: Mapped[list["AppointmentSlot"]] = relationship(back_populates="department")