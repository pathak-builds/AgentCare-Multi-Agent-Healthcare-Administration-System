"""
Tool that returns all departments from the database.
"""
from langchain_core.tools import tool
from app.database.session import SessionLocal
from app.repositories.department_repository import DepartmentRepository

@tool
def department_list() -> str:
    """
    Returns all hospital departments as a JSON list. 
    Each entry has id, name, and description.
    """
    db = SessionLocal()
    try:
        repo = DepartmentRepository(db)
        departments = repo.get_all()
        data = [
            {"id": d.id, "name": d.name, "description": d.description or ""}
            for d in departments
        ]
        # Return a formatted string (LLM can parse it)
        return str(data)
    finally:
        db.close()