from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_role
from app.services.document_service import DocumentService
from app.schemas.document import DocumentOut
from typing import List

router = APIRouter()

@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_role("patient"))
):
    service = DocumentService(db)
    return await service.upload_document(user_id=current_user.id, file=file)

@router.get("/", response_model=List[DocumentOut])
def my_documents(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("patient"))
):
    service = DocumentService(db)
    return service.get_patient_documents(user_id=current_user.id)

@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("patient", "hospital_staff", "admin"))
):
    service = DocumentService(db)
    return service.get_document(document_id)