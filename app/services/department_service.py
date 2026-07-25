from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.department import Department
from app.repositories.department_repository import DepartmentRepository
from app.utils.audit import log_audit_event

class DepartmentService:
    def __init__(self, db: Session):
        self.repo = DepartmentRepository(db)
        self.db = db

    def list_departments(self) -> list[Department]:
        return self.repo.get_all()

    def get_department(self, dept_id: str) -> Department:
        dept = self.repo.get_by_id(dept_id)
        if not dept:
            raise HTTPException(status_code=404, detail="Department not found")
        return dept

    def create_department(self, name: str, description: str | None, admin_user_id: str) -> Department:
        dept = Department(name=name, description=description)
        created = self.repo.create(dept)
        log_audit_event(self.db, admin_user_id, "department_created", f"Department '{name}' created")
        return created

    def update_department(self, dept_id: str, admin_user_id: str, **kwargs) -> Department:
        dept = self.get_department(dept_id)
        updated = self.repo.update(dept, **kwargs)
        log_audit_event(self.db, admin_user_id, "department_updated", f"Department '{updated.name}' updated")
        return updated

    def delete_department(self, dept_id: str, admin_user_id: str):
        dept = self.get_department(dept_id)
        self.repo.delete(dept)
        log_audit_event(self.db, admin_user_id, "department_deleted", f"Department '{dept.name}' deleted")