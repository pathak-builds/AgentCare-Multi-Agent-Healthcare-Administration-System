from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_role
from app.services.appointment_service import AppointmentService
from app.schemas.appointment import AppointmentOut, AppointmentCreate, AppointmentReschedule, AppointmentCancel
from typing import List

router = APIRouter()

@router.post("/", response_model=AppointmentOut, status_code=201)
def book_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("patient"))
):
    service = AppointmentService(db)
    return service.book_appointment(
        patient_id=current_user.id,  # patient user id
        slot_id=payload.slot_id,
        reason=payload.reason,
        notes=payload.notes,
        user_id=current_user.id,
    )

@router.get("/mine", response_model=List[AppointmentOut])
def my_appointments(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("patient"))
):
    service = AppointmentService(db)
    # Need to get patient id from user id; service will handle using patient repo
    # We'll add a helper in service: get_patient_appointments_by_user_id
    return service.get_patient_appointments_by_user_id(current_user.id)

@router.get("/doctor/{doctor_id}", response_model=List[AppointmentOut])
def doctor_appointments(
    doctor_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("hospital_staff", "admin"))
):
    service = AppointmentService(db)
    return service.get_doctor_appointments(doctor_id)

@router.put("/{appointment_id}/reschedule", response_model=AppointmentOut)
def reschedule_appointment(
    appointment_id: str,
    payload: AppointmentReschedule,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("patient", "hospital_staff", "admin"))
):
    service = AppointmentService(db)
    return service.reschedule_appointment(
        appointment_id=appointment_id,
        new_slot_id=payload.new_slot_id,
        user_id=current_user.id,
    )

@router.put("/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel_appointment(
    appointment_id: str,
    payload: AppointmentCancel,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("patient", "hospital_staff", "admin"))
):
    service = AppointmentService(db)
    return service.cancel_appointment(
        appointment_id=appointment_id,
        user_id=current_user.id,
        reason=payload.reason,
    )