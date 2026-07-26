"""
Tool to reschedule an appointment to a new slot.
"""
from langchain_core.tools import tool
from app.database.session import SessionLocal
from app.services.appointment_service import AppointmentService

@tool
def reschedule_appointment(appointment_id: str, new_slot_id: str, patient_id: str) -> str:
    """
    Reschedule an appointment to a new slot. Requires appointment ID, new slot ID, and patient ID.
    """
    db = SessionLocal()
    try:
        from app.models.patient import PatientProfile
        patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
        if not patient:
            return "Patient profile not found."
        service = AppointmentService(db)
        service.reschedule_appointment(
            appointment_id=appointment_id,
            new_slot_id=new_slot_id,
            user_id=patient.user_id,
        )
        return f"Appointment {appointment_id} rescheduled to slot {new_slot_id}."
    except Exception as e:
        return f"Rescheduling failed: {str(e)}"
    finally:
        db.close()