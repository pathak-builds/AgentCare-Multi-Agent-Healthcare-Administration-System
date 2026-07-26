"""
Tool to book an appointment (creates appointment + marks slot).
"""

import json

from langchain_core.tools import tool
from app.database.session import SessionLocal
from app.services.appointment_service import AppointmentService


@tool
def book_appointment(
    slot_id: str,
    patient_id: str,
    reason: str = "",
    notes: str = "",
) -> str:
    """
    Book an appointment for a given patient and slot.

    Returns a JSON string describing success or failure.
    """

    db = SessionLocal()

    try:
        service = AppointmentService(db)

        # Lookup patient profile
        from app.models.patient import PatientProfile

        patient = (
            db.query(PatientProfile)
            .filter(PatientProfile.id == patient_id)
            .first()
        )

        if not patient:
            return json.dumps(
                {
                    "status": "failure",
                    "appointment_id": None,
                    "slot_id": slot_id,
                    "message": "Patient profile not found.",
                }
            )

        appointment = service.book_appointment(
            patient_user_id=patient.user_id,
            slot_id=slot_id,
            reason=reason,
            notes=notes,
            user_id=patient.user_id,
        )

        return json.dumps(
            {
                "status": "success",
                "appointment_id": str(appointment.id),
                "slot_id": str(slot_id),
                "doctor_id": str(appointment.doctor_id),
                "appointment_time": appointment.slot.start_time.isoformat(),
                "message": (
                    f"Appointment booked successfully for "
                    f"{appointment.slot.start_time.isoformat()}"
                ),
            }
        )

    except Exception as e:

        return json.dumps(
            {
                "status": "failure",
                "appointment_id": None,
                "slot_id": slot_id,
                "message": str(e),
            }
        )

    finally:
        db.close()