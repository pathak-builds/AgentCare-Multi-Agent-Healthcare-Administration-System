"""
Tool to search doctors by department.
"""
from langchain_core.tools import tool
from app.database.session import SessionLocal
from app.repositories.doctor_repository import DoctorRepository

@tool
def doctor_search(department_id: str) -> str:
    """
    Returns a list of doctors in the given department, with IDs, names, specializations.
    """
    db = SessionLocal()
    try:
        repo = DoctorRepository(db)
        doctors = repo.get_all(department_id=department_id)
        if not doctors:
            return "No doctors found in this department."
        result = []
        for doc in doctors:
            result.append({
                "id": doc.id,
                "name": doc.user.full_name if doc.user else "Unknown",
                "specialization": doc.specialization,
            })
        return str(result)
    finally:
        db.close()