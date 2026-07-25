from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import get_current_user, require_role
from app.services.department_service import DepartmentService
from app.schemas.department import DepartmentOut, DepartmentCreate, DepartmentUpdate
from typing import List

router = APIRouter()

@router.get("/", response_model=List[DepartmentOut])
def list_departments(db: Session = Depends(get_db)):
    service = DepartmentService(db)
    return service.list_departments()

@router.post("/", response_model=DepartmentOut, status_code=201)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    service = DepartmentService(db)
    return service.create_department(
        name=payload.name,
        description=payload.description,
        admin_user_id=current_user.id,
    )

@router.put("/{department_id}", response_model=DepartmentOut)
def update_department(
    department_id: str,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    service = DepartmentService(db)
    return service.update_department(
        department_id,
        admin_user_id=current_user.id,
        name=payload.name,
        description=payload.description,
    )

@router.delete("/{department_id}", status_code=204)
def delete_department(
    department_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    service = DepartmentService(db)
    service.delete_department(department_id, admin_user_id=current_user.id)