"""
User model for authentication and role management.
"""
from sqlalchemy import Column, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel
import enum

class RoleEnum(str, enum.Enum):
    PATIENT = "patient"
    STAFF = "hospital_staff"
    ADMIN = "admin"

class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[RoleEnum] = mapped_column(SQLEnum(RoleEnum))

    # Relationships
    patient_profile: Mapped["PatientProfile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    # A staff member can be linked to a doctor record; define later
    doctor: Mapped["Doctor"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    audit_events: Mapped[list["AuditEvent"]] = relationship(back_populates="user")