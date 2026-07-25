from sqlalchemy.orm import Session
from app.models.department import Department

class DepartmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Department]:
        return self.db.query(Department).all()

    def get_by_id(self, dept_id: str) -> Department | None:
        return self.db.query(Department).filter(Department.id == dept_id).first()

    def create(self, dept: Department) -> Department:
        self.db.add(dept)
        self.db.commit()
        self.db.refresh(dept)
        return dept

    def update(self, dept: Department, **kwargs) -> Department:
        for key, value in kwargs.items():
            if value is not None:
                setattr(dept, key, value)
        self.db.commit()
        self.db.refresh(dept)
        return dept

    def delete(self, dept: Department):
        self.db.delete(dept)
        self.db.commit()