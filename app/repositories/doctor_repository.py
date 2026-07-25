from sqlalchemy.orm import Session
from app.models.doctor import Doctor
from typing import Optional

class DoctorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, department_id: Optional[str] = None) -> list[Doctor]:
        query = self.db.query(Doctor)
        if department_id:
            query = query.filter(Doctor.department_id == department_id)
        return query.all()

    def get_by_id(self, doctor_id: str) -> Doctor | None:
        return self.db.query(Doctor).filter(Doctor.id == doctor_id).first()

    def get_by_user_id(self, user_id: str) -> Doctor | None:
        return self.db.query(Doctor).filter(Doctor.user_id == user_id).first()

    def create(self, doctor: Doctor) -> Doctor:
        self.db.add(doctor)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    def update(self, doctor: Doctor, **kwargs) -> Doctor:
        for key, value in kwargs.items():
            if value is not None:
                setattr(doctor, key, value)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    def delete(self, doctor: Doctor):
        self.db.delete(doctor)
        self.db.commit()