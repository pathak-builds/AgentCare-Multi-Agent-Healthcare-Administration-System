"""
Shared pytest fixtures for AgentCare.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app as fastapi_app
print("APP TYPE =", type(fastapi_app))
print("APP =", fastapi_app)
from app.database.session import get_db
from app.models.base import Base

# ------------------------------------------------------------
# Import ALL models before Base.metadata.create_all()
# ------------------------------------------------------------

import app.models.user
import app.models.patient
import app.models.department
import app.models.doctor
import app.models.slot
import app.models.appointment
import app.models.document
import app.models.workflow
import app.models.reminder
import app.models.escalation
import app.models.audit

from app.models.user import User, RoleEnum
from app.models.patient import PatientProfile
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.slot import AppointmentSlot

from app.auth.jwt import create_access_token

from main import app

print("=" * 80)
print("APP OBJECT:", app)
print("TYPE:", type(app))
print("MODULE:", getattr(app, "__module__", None))
print("HAS dependency_overrides:", hasattr(app, "dependency_overrides"))
print("=" * 80)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

# ------------------------------------------------------------
# Test Database
# ------------------------------------------------------------

from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# ------------------------------------------------------------
# Database Fixture
# ------------------------------------------------------------

@pytest.fixture(scope="function")
def db_session():

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)

# ------------------------------------------------------------
# FastAPI Client
# ------------------------------------------------------------

@pytest.fixture(scope="function")
def client(db_session):

    def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides.clear()
    fastapi_app.dependency_overrides[get_db] = override_get_db

    with TestClient(fastapi_app) as client:
        yield client

    fastapi_app.dependency_overrides.clear()

# ------------------------------------------------------------
# Seed Database
# ------------------------------------------------------------

@pytest.fixture(scope="function")
def seed_data(db_session):

    # -------------------------
    # Admin
    # -------------------------

    admin = User(
        id=str(uuid.uuid4()),
        email="admin@test.com",
        password_hash=pwd_context.hash("admin123"),
        full_name="Admin User",
        role=RoleEnum.ADMIN,
    )

    # -------------------------
    # Patient
    # -------------------------

    patient_user = User(
        id=str(uuid.uuid4()),
        email="patient@test.com",
        password_hash=pwd_context.hash("patient123"),
        full_name="Test Patient",
        role=RoleEnum.PATIENT,
    )

    patient_profile = PatientProfile(
        id=str(uuid.uuid4()),
        user_id=patient_user.id,
    )

    # -------------------------
    # Department
    # -------------------------

    department = Department(
        id=str(uuid.uuid4()),
        name="Cardiology",
        description="Heart Department",
    )

    # -------------------------
    # Doctor User
    # -------------------------

    doctor_user = User(
        id=str(uuid.uuid4()),
        email="doctor@test.com",
        password_hash=pwd_context.hash("doctor123"),
        full_name="Dr Heart",
        role=RoleEnum.STAFF,
    )

    # -------------------------
    # Doctor
    # -------------------------

    doctor = Doctor(
        id=str(uuid.uuid4()),
        user_id=doctor_user.id,
        department_id=department.id,
        specialization="Cardiologist",
    )

    # -------------------------
    # Appointment Slot
    # -------------------------

    start = datetime.now(timezone.utc) + timedelta(days=1)

    slot = AppointmentSlot(
        id=str(uuid.uuid4()),
        doctor_id=doctor.id,
        department_id=department.id,
        start_time=start,
        end_time=start + timedelta(hours=1),
        is_booked=False,
    )

    db_session.add_all(
        [
            admin,
            patient_user,
            patient_profile,
            department,
            doctor_user,
            doctor,
            slot,
        ]
    )

    db_session.commit()

    for obj in (
        admin,
        patient_user,
        patient_profile,
        department,
        doctor_user,
        doctor,
        slot,
    ):
        db_session.refresh(obj)

    return {
        "admin": admin,
        "patient_user": patient_user,
        "patient_profile": patient_profile,
        "department": department,
        "doctor_user": doctor_user,
        "doctor": doctor,
        "slot": slot,
    }

# ------------------------------------------------------------
# JWT Fixtures
# ------------------------------------------------------------

@pytest.fixture
def patient_token(seed_data):
    return create_access_token(
        seed_data["patient_user"].id,
        "patient",
    )


@pytest.fixture
def admin_token(seed_data):
    return create_access_token(
        seed_data["admin"].id,
        "admin",
    )