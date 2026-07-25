"""
Documents uploaded by patients (lab reports, prescriptions, etc.).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .patient import PatientProfile

class PatientDocument(BaseModel):
    __tablename__ = "patient_documents"

    patient_id: Mapped[str] = mapped_column(ForeignKey("patient_profiles.id"))
    filename: Mapped[str] = mapped_column(String(255))
    original_filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(50))  # pdf, docx, png, jpeg
    file_size: Mapped[int]  # bytes
    sha256_checksum: Mapped[str] = mapped_column(String(64), index=True)
    classification: Mapped[str] = mapped_column(String(50), nullable=True)  # blood_report, ecg, mri, ct_scan, prescription, insurance, other
    extracted_text: Mapped[str] = mapped_column(Text, nullable=True)
    metadata_: Mapped[str] = mapped_column("metadata", Text, nullable=True)  # JSON string
    upload_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    patient: Mapped["PatientProfile"] = relationship(back_populates="documents")