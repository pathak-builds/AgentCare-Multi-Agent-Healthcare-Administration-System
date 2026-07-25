from sqlalchemy.orm import Session
from app.models.patient import PatientProfile

class PatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: str) -> PatientProfile | None:
        return self.db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()

    def create(self, profile: PatientProfile) -> PatientProfile:
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile