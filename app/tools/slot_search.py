"""
Tool to find available slots for a doctor.
"""
from langchain_core.tools import tool
from app.database.session import SessionLocal
from app.repositories.slot_repository import SlotRepository

@tool
def slot_search(doctor_id: str) -> str:
    """
    Returns a list of available (unbooked, future) slots for the given doctor.
    Each slot shows id, start_time, end_time.
    """
    db = SessionLocal()
    try:
        repo = SlotRepository(db)
        slots = repo.get_available_by_doctor(doctor_id)
        if not slots:
            return "No available slots for this doctor."
        result = []
        for s in slots:
            result.append({
                "id": s.id,
                "start": s.start_time.isoformat(),
                "end": s.end_time.isoformat(),
            })
        return str(result)
    finally:
        db.close()