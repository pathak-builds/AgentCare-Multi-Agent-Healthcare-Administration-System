"""
Seeds the database with initial sample data: admin, staff, patient,
departments, doctors, and appointment slots.
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database.session import SessionLocal, engine
from app.models.base import Base
from app.models import (
    User, PatientProfile, Department, Doctor, AppointmentSlot, RoleEnum
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    params = dict(kwargs)
    if defaults:
        params.update(defaults)
    instance = model(**params)
    session.add(instance)
    session.commit()
    return instance, True

def seed():
    Base.metadata.create_all(bind=engine)  # ensure tables exist
    db: Session = SessionLocal()
    try:
        # ---- Users ----
        admin_user, _ = get_or_create(
            db, User,
            email="admin@agentcare.com",
            defaults={
                "password_hash": pwd_context.hash("admin123"),
                "full_name": "System Administrator",
                "role": RoleEnum.ADMIN,
            }
        )
        staff_user, _ = get_or_create(
            db, User,
            email="staff@agentcare.com",
            defaults={
                "password_hash": pwd_context.hash("staff123"),
                "full_name": "Jane Staff",
                "role": RoleEnum.STAFF,
            }
        )
        patient_user, _ = get_or_create(
            db, User,
            email="patient@agentcare.com",
            defaults={
                "password_hash": pwd_context.hash("patient123"),
                "full_name": "John Patient",
                "role": RoleEnum.PATIENT,
            }
        )

        # Patient profile
        patient_profile, _ = get_or_create(
            db, PatientProfile,
            user_id=patient_user.id,
            defaults={
                "date_of_birth": datetime(1990, 5, 15).date(),
                "phone": "+1-555-0100",
                "address": "123 Main St, Anytown",
                "emergency_contact": "+1-555-0199",
            }
        )

        # ---- Departments ----
        dept_names = ["Cardiology", "Neurology", "Orthopedics", "Dermatology", "ENT", "Pediatrics", "General Medicine"]
        departments = {}
        for name in dept_names:
            dept, _ = get_or_create(db, Department, name=name)
            departments[name] = dept

        # ---- Doctors (staff user is one; create a few more) ----
        # We'll create a doctor linked to staff_user (if not exists)
        doctor1, _ = get_or_create(
            db, Doctor,
            user_id=staff_user.id,
            defaults={
                "department_id": departments["General Medicine"].id,
                "specialization": "Family Medicine",
                "license_number": "LIC-001",
            }
        )

        # Additional doctors for other departments (no user accounts, but we can have dummy users)
        dept_doctor_map = {
            "Cardiology": ("Dr. Heart", "cardio@agentcare.com", "CARD-001"),
            "Neurology": ("Dr. Brain", "neuro@agentcare.com", "NEURO-001"),
            "Orthopedics": ("Dr. Bone", "ortho@agentcare.com", "ORTHO-001"),
            "Dermatology": ("Dr. Skin", "derm@agentcare.com", "DERM-001"),
            "ENT": ("Dr. Ear", "ent@agentcare.com", "ENT-001"),
            "Pediatrics": ("Dr. Kid", "peds@agentcare.com", "PEDS-001"),
        }
        doctors = {doctor1.user.email: doctor1}
        for dept_name, (full_name, email, lic) in dept_doctor_map.items():
            # create user for doctor
            doc_user, _ = get_or_create(
                db, User,
                email=email,
                defaults={
                    "password_hash": pwd_context.hash("doctor123"),
                    "full_name": full_name,
                    "role": RoleEnum.STAFF,
                }
            )
            doctor, _ = get_or_create(
                db, Doctor,
                user_id=doc_user.id,
                defaults={
                    "department_id": departments[dept_name].id,
                    "specialization": dept_name,
                    "license_number": lic,
                }
            )
            doctors[email] = doctor

        # ---- Appointment Slots (next 7 days, 9am-5pm, 1h slots) ----
        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0) + timedelta(days=1)
        for doctor in doctors.values():
            for day_offset in range(7):
                day = now + timedelta(days=day_offset)
                # Only weekdays
                if day.weekday() >= 5:
                    continue
                for hour in range(9, 17):
                    start = day.replace(hour=hour)
                    end = start + timedelta(hours=1)
                    # check if slot exists
                    exists = db.query(AppointmentSlot).filter_by(
                        doctor_id=doctor.id, start_time=start
                    ).first()
                    if not exists:
                        slot = AppointmentSlot(
                            id=str(uuid.uuid4()),
                            doctor_id=doctor.id,
                            department_id=doctor.department_id,
                            start_time=start,
                            end_time=end,
                            is_booked=False,
                        )
                        db.add(slot)

        db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()