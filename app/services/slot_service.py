from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.slot import AppointmentSlot
from app.repositories.slot_repository import SlotRepository
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.department_repository import DepartmentRepository
from app.utils.audit import log_audit_event
from datetime import datetime

class SlotService:
    def __init__(self, db: Session):
        self.repo = SlotRepository(db)
        self.doctor_repo = DoctorRepository(db)
        self.dept_repo = DepartmentRepository(db)
        self.db = db

    def list_slots(self, doctor_id: str | None = None, department_id: str | None = None) -> list[AppointmentSlot]:
        return self.repo.get_all(doctor_id, department_id)

    def list_available_slots(self, doctor_id: str) -> list[AppointmentSlot]:
        if not self.doctor_repo.get_by_id(doctor_id):
            raise HTTPException(status_code=404, detail="Doctor not found")
        return self.repo.get_available_by_doctor(doctor_id)

    def create_slot(self, doctor_id: str, department_id: str, start_time: datetime, end_time: datetime, user_id: str) -> AppointmentSlot:
        # Validate doctor and department exist
        if not self.doctor_repo.get_by_id(doctor_id):
            raise HTTPException(status_code=404, detail="Doctor not found")
        if not self.dept_repo.get_by_id(department_id):
            raise HTTPException(status_code=404, detail="Department not found")
        if start_time >= end_time:
            raise HTTPException(status_code=400, detail="End time must be after start time")

        slot = AppointmentSlot(
            doctor_id=doctor_id,
            department_id=department_id,
            start_time=start_time,
            end_time=end_time,
            is_booked=False,
        )
        created = self.repo.create(slot)
        log_audit_event(self.db, user_id, "slot_created", f"Slot created for doctor {doctor_id} at {start_time}")
        return created

    def delete_slot(self, slot_id: str, user_id: str):
        slot = self.repo.get_by_id(slot_id)
        if not slot:
            raise HTTPException(status_code=404, detail="Slot not found")
        self.repo.delete(slot)
        log_audit_event(self.db, user_id, "slot_deleted", f"Slot {slot_id} deleted")