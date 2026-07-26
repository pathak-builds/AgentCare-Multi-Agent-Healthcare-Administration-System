"""
Tool to look up patient profile from the database.
"""
from langchain_core.tools import tool
from app.database.session import SessionLocal
from app.repositories.patient_repository import PatientRepository

@tool
def patient_lookup(user_id: str) -> str:
    """Look up a patient by user ID. Returns patient details or 'Not found'."""
    db = SessionLocal()
    try:
        repo = PatientRepository(db)
        patient = repo.get_by_user_id(user_id)
        if not patient:
            return "Patient not found"
        return (
            f"Patient: {patient.user.full_name}\n"
            f"DOB: {patient.date_of_birth}\n"
            f"Phone: {patient.phone}\n"
            f"Address: {patient.address}"
        )
    finally:
        db.close()