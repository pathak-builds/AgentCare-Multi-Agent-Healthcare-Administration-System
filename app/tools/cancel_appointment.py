"""
Tool to cancel an appointment.
"""
from langchain_core.tools import tool
from app.database.session import SessionLocal
from app.services.appointment_service import AppointmentService

@tool
def cancel_appointment(appointment_id: str, patient_id: str) -> str:
    """
    Cancel an existing appointment. Requires appointment ID and patient ID.
    """
    db = SessionLocal()
    try:
        from app.models.patient import PatientProfile
        patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
        if not patient:
            return "Patient profile not found."
        service = AppointmentService(db)
        service.cancel_appointment(
            appointment_id=appointment_id,
            user_id=patient.user_id,
        )
        return f"Appointment {appointment_id} cancelled successfully."
    except Exception as e:
        return f"Cancellation failed: {str(e)}"
    finally:
        db.close()