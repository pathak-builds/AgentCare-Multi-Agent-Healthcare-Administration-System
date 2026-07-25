from sqlalchemy.orm import Session
from app.models.appointment import Appointment, AppointmentStatus

class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, appointment_id: str) -> Appointment | None:
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def get_by_patient(self, patient_id: str) -> list[Appointment]:
        return self.db.query(Appointment).filter(Appointment.patient_id == patient_id).order_by(Appointment.created_at.desc()).all()

    def get_by_doctor(self, doctor_id: str) -> list[Appointment]:
        return self.db.query(Appointment).filter(Appointment.doctor_id == doctor_id).order_by(Appointment.created_at.desc()).all()

    def create(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def update(self, appointment: Appointment, **kwargs) -> Appointment:
        for key, value in kwargs.items():
            setattr(appointment, key, value)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def delete(self, appointment: Appointment):
        self.db.delete(appointment)
        self.db.commit()