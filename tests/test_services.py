"""
Tests for the service layer.
"""

import io

import pytest
from fastapi import UploadFile, HTTPException

from app.services.appointment_service import AppointmentService
from app.services.document_service import DocumentService
from app.repositories.slot_repository import SlotRepository
from app.repositories.appointment_repository import AppointmentRepository
from app.models.appointment import AppointmentStatus


# ---------------------------------------------------------------------
# Appointment Booking
# ---------------------------------------------------------------------

def test_book_appointment(seed_data, db_session):

    service = AppointmentService(db_session)

    appointment = service.book_appointment(
        patient_user_id=seed_data["patient_user"].id,
        slot_id=seed_data["slot"].id,
        reason="Routine Checkup",
        notes="Patient requested morning appointment",
        user_id=seed_data["patient_user"].id,
    )

    assert appointment is not None
    assert appointment.id is not None
    assert appointment.status == AppointmentStatus.SCHEDULED

    slot_repo = SlotRepository(db_session)

    slot = slot_repo.get_by_id(seed_data["slot"].id)

    assert slot.is_booked is True

    appointment_repo = AppointmentRepository(db_session)

    appointments = appointment_repo.get_by_patient(
        seed_data["patient_profile"].id
    )

    assert len(appointments) == 1

    # Double booking should fail
    with pytest.raises(HTTPException):
        service.book_appointment(
            patient_user_id=seed_data["patient_user"].id,
            slot_id=seed_data["slot"].id,
            reason="Another booking",
            notes="",
            user_id=seed_data["patient_user"].id,
        )


# ---------------------------------------------------------------------
# Appointment Cancellation
# ---------------------------------------------------------------------

def test_cancel_appointment(seed_data, db_session):

    service = AppointmentService(db_session)

    appointment = service.book_appointment(
        patient_user_id=seed_data["patient_user"].id,
        slot_id=seed_data["slot"].id,
        reason="Checkup",
        notes="",
        user_id=seed_data["patient_user"].id,
    )

    cancelled = service.cancel_appointment(
        appointment.id,
        seed_data["patient_user"].id,
        reason="Unavailable",
    )

    assert cancelled.status == AppointmentStatus.CANCELLED

    slot_repo = SlotRepository(db_session)

    slot = slot_repo.get_by_id(seed_data["slot"].id)

    assert slot.is_booked is False


# ---------------------------------------------------------------------
# Get Patient Appointments
# ---------------------------------------------------------------------

def test_get_patient_appointments(seed_data, db_session):

    service = AppointmentService(db_session)

    service.book_appointment(
        patient_user_id=seed_data["patient_user"].id,
        slot_id=seed_data["slot"].id,
        reason="Checkup",
        notes="",
        user_id=seed_data["patient_user"].id,
    )

    appointments = service.get_patient_appointments_by_user_id(
        seed_data["patient_user"].id,
    )

    assert len(appointments) == 1
    assert appointments[0].status == AppointmentStatus.SCHEDULED


# ---------------------------------------------------------------------
# Document Upload
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_document_upload(seed_data, db_session):

    service = DocumentService(db_session)

    content = b"Fake PDF content"

    upload = UploadFile(
        filename="report.pdf",
        file=io.BytesIO(content),
    )

    document = await service.upload_document(
        seed_data["patient_user"].id,
        upload,
    )

    assert document.id is not None
    assert document.original_filename == "report.pdf"
    assert document.file_type == "pdf"
    assert document.sha256_checksum is not None

    duplicate = UploadFile(
        filename="duplicate.pdf",
        file=io.BytesIO(content),
    )

    with pytest.raises(HTTPException):
        await service.upload_document(
            seed_data["patient_user"].id,
            duplicate,
        )


# ---------------------------------------------------------------------
# Get Patient Documents
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_patient_documents(seed_data, db_session):

    service = DocumentService(db_session)

    upload = UploadFile(
        filename="report.pdf",
        file=io.BytesIO(b"Sample PDF"),
    )

    await service.upload_document(
        seed_data["patient_user"].id,
        upload,
    )

    documents = service.get_patient_documents(
        seed_data["patient_user"].id,
    )

    assert len(documents) == 1
    assert documents[0].original_filename == "report.pdf"


# ---------------------------------------------------------------------
# Invalid Document Lookup
# ---------------------------------------------------------------------

def test_get_document_not_found(db_session):

    service = DocumentService(db_session)

    with pytest.raises(HTTPException):
        service.get_document("invalid-document-id")


# ---------------------------------------------------------------------
# Invalid Text Extraction
# ---------------------------------------------------------------------

def test_extract_text_invalid_document(db_session):

    service = DocumentService(db_session)

    with pytest.raises(HTTPException):
        service.extract_text("invalid-document-id")