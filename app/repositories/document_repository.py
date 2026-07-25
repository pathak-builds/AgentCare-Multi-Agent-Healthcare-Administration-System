from sqlalchemy.orm import Session
from app.models.document import PatientDocument

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, doc_id: str) -> PatientDocument | None:
        return self.db.query(PatientDocument).filter(PatientDocument.id == doc_id).first()

    def get_by_patient(self, patient_id: str) -> list[PatientDocument]:
        return self.db.query(PatientDocument).filter(PatientDocument.patient_id == patient_id).order_by(PatientDocument.upload_date.desc()).all()

    def create(self, document: PatientDocument) -> PatientDocument:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_by_checksum(self, sha256: str) -> PatientDocument | None:
        return self.db.query(PatientDocument).filter(PatientDocument.sha256_checksum == sha256).first()