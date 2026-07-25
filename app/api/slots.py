from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_role
from app.services.slot_service import SlotService
from app.schemas.slot import SlotOut, SlotCreate
from typing import List, Optional

router = APIRouter()

@router.get("/", response_model=List[SlotOut])
def list_slots(
    doctor_id: Optional[str] = Query(None),
    department_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = SlotService(db)
    return service.list_slots(doctor_id, department_id)

@router.get("/available/{doctor_id}", response_model=List[SlotOut])
def available_slots(
    doctor_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = SlotService(db)
    return service.list_available_slots(doctor_id)

@router.post("/", response_model=SlotOut, status_code=201)
def create_slot(
    payload: SlotCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin", "hospital_staff"))
):
    service = SlotService(db)
    return service.create_slot(
        doctor_id=payload.doctor_id,
        department_id=payload.department_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        user_id=current_user.id,
    )

@router.delete("/{slot_id}", status_code=204)
def delete_slot(
    slot_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    service = SlotService(db)
    service.delete_slot(slot_id, user_id=current_user.id)