from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.doctor import Doctor
from app.models.user import User
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.user_repository import UserRepository
from app.utils.audit import log_audit_event

class DoctorService:
    def __init__(self, db: Session):
        self.repo = DoctorRepository(db)
        self.user_repo = UserRepository(db)
        self.db = db

    def list_doctors(self, department_id: str | None = None) -> list[Doctor]:
        return self.repo.get_all(department_id)

    def get_doctor(self, doctor_id: str) -> Doctor:
        doctor = self.repo.get_by_id(doctor_id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return doctor

    def create_doctor(self, user_email: str, department_id: str, specialization: str | None, license_number: str | None, admin_user_id: str) -> Doctor:
        user = self.user_repo.get_by_email(user_email)
        if not user:
            raise HTTPException(status_code=400, detail="User with this email does not exist")
        if user.role.value != "hospital_staff":
            raise HTTPException(status_code=400, detail="User must have role 'hospital_staff'")
        if self.repo.get_by_user_id(user.id):
            raise HTTPException(status_code=400, detail="Doctor profile already exists for this user")

        doctor = Doctor(
            user_id=user.id,
            department_id=department_id,
            specialization=specialization,
            license_number=license_number,
        )
        created = self.repo.create(doctor)
        log_audit_event(self.db, admin_user_id, "doctor_created", f"Doctor '{user.full_name}' added to department {department_id}")
        return created

    def update_doctor(self, doctor_id: str, admin_user_id: str, **kwargs) -> Doctor:
        doctor = self.get_doctor(doctor_id)
        updated = self.repo.update(doctor, **kwargs)
        log_audit_event(self.db, admin_user_id, "doctor_updated", f"Doctor updated")
        return updated

    def delete_doctor(self, doctor_id: str, admin_user_id: str):
        doctor = self.get_doctor(doctor_id)
        self.repo.delete(doctor)
        log_audit_event(self.db, admin_user_id, "doctor_deleted", f"Doctor '{doctor.user.full_name}' deleted")