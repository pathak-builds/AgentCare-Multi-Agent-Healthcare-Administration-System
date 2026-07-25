from sqlalchemy.orm import Session
from app.models.slot import AppointmentSlot
from typing import Optional
from datetime import datetime

class SlotRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, slot_id: str) -> AppointmentSlot | None:
        return self.db.query(AppointmentSlot).filter(AppointmentSlot.id == slot_id).first()

    def get_available_by_doctor(self, doctor_id: str) -> list[AppointmentSlot]:
        return self.db.query(AppointmentSlot).filter(
            AppointmentSlot.doctor_id == doctor_id,
            AppointmentSlot.is_booked == False,
            AppointmentSlot.start_time > datetime.utcnow()
        ).order_by(AppointmentSlot.start_time).all()

    def get_all(self, doctor_id: Optional[str] = None, department_id: Optional[str] = None) -> list[AppointmentSlot]:
        query = self.db.query(AppointmentSlot)
        if doctor_id:
            query = query.filter(AppointmentSlot.doctor_id == doctor_id)
        if department_id:
            query = query.filter(AppointmentSlot.department_id == department_id)
        return query.order_by(AppointmentSlot.start_time).all()

    def create(self, slot: AppointmentSlot) -> AppointmentSlot:
        self.db.add(slot)
        self.db.commit()
        self.db.refresh(slot)
        return slot

    def update(self, slot: AppointmentSlot, **kwargs) -> AppointmentSlot:
        for key, value in kwargs.items():
            setattr(slot, key, value)
        self.db.commit()
        self.db.refresh(slot)
        return slot

    def delete(self, slot: AppointmentSlot):
        self.db.delete(slot)
        self.db.commit()