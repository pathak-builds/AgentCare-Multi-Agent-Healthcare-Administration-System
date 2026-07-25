from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_role
from app.services.doctor_service import DoctorService
from app.schemas.doctor import DoctorOut, DoctorCreate, DoctorUpdate
from typing import List, Optional

router = APIRouter()

@router.get("/", response_model=List[DoctorOut])
def list_doctors(
    department_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = DoctorService(db)
    return service.list_doctors(department_id)

@router.post("/", response_model=DoctorOut, status_code=201)
def create_doctor(
    payload: DoctorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    service = DoctorService(db)
    return service.create_doctor(
        user_email=payload.user_email,
        department_id=payload.department_id,
        specialization=payload.specialization,
        license_number=payload.license_number,
        admin_user_id=current_user.id,
    )

@router.put("/{doctor_id}", response_model=DoctorOut)
def update_doctor(
    doctor_id: str,
    payload: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    service = DoctorService(db)
    return service.update_doctor(
        doctor_id,
        admin_user_id=current_user.id,
        specialization=payload.specialization,
        license_number=payload.license_number,
        department_id=payload.department_id,
    )

@router.delete("/{doctor_id}", status_code=204)
def delete_doctor(
    doctor_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    service = DoctorService(db)
    service.delete_doctor(doctor_id, admin_user_id=current_user.id)