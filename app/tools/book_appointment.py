"""
Tool to book an appointment (creates appointment + marks slot).
"""
from langchain_core.tools import tool
from app.database.session import SessionLocal
from app.services.appointment_service import AppointmentService

@tool
def book_appointment(slot_id: str, patient_id: str, reason: str = "", notes: str = "") -> str:
    """
    Book an appointment for a given patient and slot. Returns confirmation or error.
    """
    db = SessionLocal()
    try:
        service = AppointmentService(db)
        # The service expects user_id for audit, we pass patient_id as user_id (patient's user id)
        # but the service method expects user_id as the user performing the action.
        # We'll create a simple wrapper: the booking tool will use the patient's user_id.
        # For that we need to map patient_id (which is a profile ID) to user_id.
        # Actually, in our previous service, book_appointment expects patient_id (profile ID) as first arg,
        # and user_id for audit. We have both: patient_id is the profile ID, but we also need the user's actual user_id.
        # The tool only receives the patient_id (profile ID). We'll look up the user_id from the patient profile.
        from app.models.patient import PatientProfile
        patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
        if not patient:
            return "Patient profile not found."
        appointment = service.book_appointment(
            patient_user_id=patient.user_id,
            slot_id=slot_id,
            reason=reason,
            notes=notes,
            user_id=patient.user_id,  # audit as the patient user
        )
        return f"Appointment booked successfully. ID: {appointment.id}, Date: {appointment.slot.start_time.isoformat()}"
    except Exception as e:
        return f"Booking failed: {str(e)}"
    finally:
        db.close()