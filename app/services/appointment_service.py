from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.appointment import Appointment, AppointmentStatus
from app.models.slot import AppointmentSlot
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.slot_repository import SlotRepository
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.patient_repository import PatientRepository
from app.utils.audit import log_audit_event
from datetime import datetime

class AppointmentService:
    def __init__(self, db: Session):
        self.repo = AppointmentRepository(db)
        self.slot_repo = SlotRepository(db)
        self.doctor_repo = DoctorRepository(db)
        self.patient_repo = PatientRepository(db)
        self.db = db

    def book_appointment(self, patient_id: str, slot_id: str, reason: str | None, notes: str | None, user_id: str) -> Appointment:
        # Ensure patient profile exists
        patient = self.patient_repo.get_by_user_id(patient_id)  # we'll add that method
        if not patient:
            raise HTTPException(status_code=400, detail="Patient profile not found")

        slot = self.slot_repo.get_by_id(slot_id)
        if not slot:
            raise HTTPException(status_code=404, detail="Slot not found")
        if slot.is_booked:
            raise HTTPException(status_code=409, detail="Slot already booked")
        if slot.start_time < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Cannot book a past slot")

        # Mark slot as booked
        slot.is_booked = True
        self.slot_repo.update(slot, is_booked=True)

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=slot.doctor_id,
            slot_id=slot.id,
            status=AppointmentStatus.SCHEDULED,
            reason=reason,
            notes=notes,
        )
        created = self.repo.create(appointment)
        log_audit_event(self.db, user_id, "appointment_booked", f"Appointment booked for patient {patient.id} with doctor {slot.doctor_id}")
        return created

    def reschedule_appointment(self, appointment_id: str, new_slot_id: str, user_id: str) -> Appointment:
        appointment = self.repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        if appointment.status not in (AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED):
            raise HTTPException(status_code=400, detail="Only scheduled/confirmed appointments can be rescheduled")

        new_slot = self.slot_repo.get_by_id(new_slot_id)
        if not new_slot:
            raise HTTPException(status_code=404, detail="New slot not found")
        if new_slot.is_booked:
            raise HTTPException(status_code=409, detail="New slot already booked")
        if new_slot.start_time < datetime.utcnow():
            raise HTTPException(status_code=400, detail="New slot is in the past")

        # Free old slot
        old_slot = appointment.slot
        old_slot.is_booked = False
        self.slot_repo.update(old_slot, is_booked=False)

        # Book new slot
        new_slot.is_booked = True
        self.slot_repo.update(new_slot, is_booked=True)

        # Update appointment
        appointment.slot_id = new_slot.id
        appointment.doctor_id = new_slot.doctor_id
        appointment.status = AppointmentStatus.RESCHEDULED
        updated = self.repo.update(appointment, slot_id=new_slot.id, doctor_id=new_slot.doctor_id, status=AppointmentStatus.RESCHEDULED)
        log_audit_event(self.db, user_id, "appointment_rescheduled", f"Appointment {appointment.id} rescheduled to slot {new_slot.id}")
        return updated

    def cancel_appointment(self, appointment_id: str, user_id: str, reason: str | None = None) -> Appointment:
        appointment = self.repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        if appointment.status == AppointmentStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Appointment already cancelled")

        # Free slot
        slot = appointment.slot
        slot.is_booked = False
        self.slot_repo.update(slot, is_booked=False)

        appointment.status = AppointmentStatus.CANCELLED
        if reason:
            appointment.reason = reason  # store cancellation reason
        updated = self.repo.update(appointment, status=AppointmentStatus.CANCELLED, reason=reason)
        log_audit_event(self.db, user_id, "appointment_cancelled", f"Appointment {appointment.id} cancelled")
        return updated

    def get_patient_appointments(self, patient_id: str) -> list[Appointment]:
        return self.repo.get_by_patient(patient_id)

    def get_doctor_appointments(self, doctor_id: str) -> list[Appointment]:
        return self.repo.get_by_doctor(doctor_id)
    
    def get_patient_appointments_by_user_id(self, user_id: str) -> list[Appointment]:
        patient = self.patient_repo.get_by_user_id(user_id)
        if not patient:
            raise HTTPException(
                status_code=400,
                detail="Patient profile not found"
            )
        return self.repo.get_by_patient(patient.id)