from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.models.document import PatientDocument
from app.repositories.document_repository import DocumentRepository
from app.repositories.patient_repository import PatientRepository
from app.utils.audit import log_audit_event
import hashlib
import os
import uuid
from datetime import datetime
from app.config import settings

class DocumentService:
    def __init__(self, db: Session):
        self.repo = DocumentRepository(db)
        self.patient_repo = PatientRepository(db)
        self.db = db
        self.upload_dir = settings.base_dir / "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    def _compute_sha256(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    async def upload_document(self, user_id: str, file: UploadFile) -> PatientDocument:
        # Validate patient profile
        patient = self.patient_repo.get_by_user_id(user_id)
        if not patient:
            raise HTTPException(status_code=400, detail="Patient profile not found")

        # Allowed extensions
        allowed_exts = {"pdf", "docx", "png", "jpeg", "jpg"}
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in allowed_exts:
            raise HTTPException(status_code=400, detail=f"File type .{ext} not allowed. Allowed: {', '.join(allowed_exts)}")

        # Save file with unique name
        unique_name = f"{uuid.uuid4()}.{ext}"
        file_path = self.upload_dir / unique_name
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        file_size = len(contents)
        checksum = self._compute_sha256(str(file_path))

        # Check for duplicate
        existing = self.repo.get_by_checksum(checksum)
        if existing:
            os.remove(file_path)  # cleanup duplicate file
            raise HTTPException(status_code=409, detail="Document already uploaded (checksum match)")

        doc = PatientDocument(
            patient_id=patient.id,
            filename=unique_name,
            original_filename=file.filename,
            file_path=str(file_path),
            file_type=ext,
            file_size=file_size,
            sha256_checksum=checksum,
            upload_date=datetime.utcnow(),
        )
        created = self.repo.create(doc)
        log_audit_event(self.db, user_id, "document_uploaded", f"Document '{file.filename}' uploaded")
        return created

    def get_patient_documents(self, user_id: str) -> list[PatientDocument]:
        patient = self.patient_repo.get_by_user_id(user_id)
        if not patient:
            raise HTTPException(status_code=400, detail="Patient profile not found")
        return self.repo.get_by_patient(patient.id)

    def get_document(self, doc_id: str) -> PatientDocument:
        doc = self.repo.get_by_id(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc