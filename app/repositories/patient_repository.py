"""
Repository for patient profile operations.
"""
from sqlalchemy.orm import Session
from app.models.patient import PatientProfile

class PatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, profile: PatientProfile) -> PatientProfile:
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile