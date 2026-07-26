"""
Tools for generating reminders and follow-up actions.
"""

import json
from datetime import datetime, timedelta

from langchain_core.tools import tool

from app.database.session import SessionLocal

from app.models.appointment import Appointment, AppointmentStatus
from app.models.slot import AppointmentSlot
from app.models.reminder import Reminder
from app.utils.audit import log_audit_event


@tool
def get_appointments_without_reminders(patient_id: str) -> str:
    """
    Return future appointments that do not yet have reminders.
    """

    db = SessionLocal()

    try:

        now = datetime.utcnow()

        appointments = (
            db.query(Appointment)
            .join(AppointmentSlot)
            .filter(
                Appointment.patient_id == patient_id,
                Appointment.status.in_(
                    [
                        AppointmentStatus.SCHEDULED,
                        AppointmentStatus.CONFIRMED,
                    ]
                ),
                AppointmentSlot.start_time > now,
            )
            .all()
        )

        pending = []

        for appointment in appointments:

            # Skip appointments that already have reminders
            if appointment.reminder:
                continue

            pending.append(
                {
                    "appointment_id": appointment.id,
                    "slot_start": appointment.slot.start_time.isoformat(),
                    "reminder_time": (
                        appointment.slot.start_time
                        - timedelta(hours=24)
                    ).isoformat(),
                    "doctor_name": (
                        appointment.doctor.user.full_name
                        if appointment.doctor
                        and appointment.doctor.user
                        else "Unknown"
                    ),
                }
            )

        if not pending:
            return json.dumps(
                {
                    "appointments": [],
                    "message": "No appointments without reminders.",
                }
            )

        return json.dumps(
            {
                "appointments": pending
            }
        )

    finally:
        db.close()


@tool
def create_reminder(
    appointment_id: str,
    reminder_time_str: str,
    message: str,
) -> str:
    """
    Create a reminder for an appointment.
    """

    db = SessionLocal()

    try:

        appointment = (
            db.query(Appointment)
            .filter(Appointment.id == appointment_id)
            .first()
        )

        if not appointment:
            return "Appointment not found."

        if appointment.reminder:
            return "Reminder already exists."

        reminder_time = datetime.fromisoformat(reminder_time_str)

        reminder = Reminder(
            appointment_id=appointment.id,
            reminder_time=reminder_time,
            message=message,
            is_sent=False,
        )

        db.add(reminder)
        db.commit()

        return (
            f"Reminder created successfully for appointment "
            f"{appointment.id}."
        )

    except Exception as e:

        db.rollback()

        return f"Failed to create reminder: {e}"

    finally:

        db.close()


@tool
def log_followup_action(
    workflow_id: str,
    description: str,
) -> str:
    """
    Log a follow-up action.
    """

    db = SessionLocal()

    try:

        log_audit_event(
            db=db,
            user_id=None,
            event_type="followup_action",
            description=f"Workflow {workflow_id}: {description}",
        )

        return "Follow-up action logged."

    except Exception as e:

        db.rollback()

        return f"Failed to log follow-up action: {e}"

    finally:

        db.close()