"""
Repository layer tests.
"""

from app.models.department import Department
from app.repositories.department_repository import DepartmentRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.slot_repository import SlotRepository


# ---------------------------------------------------------------------
# Department Repository
# ---------------------------------------------------------------------

def test_department_create_get_update_delete(db_session):

    repo = DepartmentRepository(db_session)

    department = Department(
        name="Neurology",
        description="Brain and Nervous System",
    )

    created = repo.create(department)

    assert created.id is not None

    fetched = repo.get_by_id(created.id)

    assert fetched is not None
    assert fetched.name == "Neurology"

    departments = repo.get_all()

    assert len(departments) == 1

    updated = repo.update(
        fetched,
        name="Advanced Neurology",
        description="Updated Description",
    )

    assert updated.name == "Advanced Neurology"

    repo.delete(updated)

    assert repo.get_by_id(created.id) is None


# ---------------------------------------------------------------------
# Slot Repository
# ---------------------------------------------------------------------

def test_get_available_slots(seed_data, db_session):

    repo = SlotRepository(db_session)

    doctor_id = seed_data["doctor"].id

    available_slots = repo.get_available_by_doctor(
        doctor_id
    )

    assert len(available_slots) == 1

    slot = available_slots[0]

    assert slot.is_booked is False

    slot.is_booked = True

    db_session.commit()

    available_slots = repo.get_available_by_doctor(
        doctor_id
    )

    assert len(available_slots) == 0


# ---------------------------------------------------------------------
# Patient Repository
# ---------------------------------------------------------------------

def test_get_patient_by_user_id(seed_data, db_session):

    repo = PatientRepository(db_session)

    patient = repo.get_by_user_id(
        seed_data["patient_user"].id
    )

    assert patient is not None
    assert patient.user_id == seed_data["patient_user"].id
    assert patient.user.email == "patient@test.com"


# ---------------------------------------------------------------------
# Department Repository (Empty DB)
# ---------------------------------------------------------------------

def test_get_all_departments_empty(db_session):

    repo = DepartmentRepository(db_session)

    departments = repo.get_all()

    assert departments == []


# ---------------------------------------------------------------------
# Invalid Department Lookup
# ---------------------------------------------------------------------

def test_get_invalid_department(db_session):

    repo = DepartmentRepository(db_session)

    department = repo.get_by_id("invalid-id")

    assert department is None


# ---------------------------------------------------------------------
# Invalid Patient Lookup
# ---------------------------------------------------------------------

def test_invalid_patient_lookup(db_session):

    repo = PatientRepository(db_session)

    patient = repo.get_by_user_id("does-not-exist")

    assert patient is None


# ---------------------------------------------------------------------
# No Slots For Unknown Doctor
# ---------------------------------------------------------------------

def test_no_slots_unknown_doctor(db_session):

    repo = SlotRepository(db_session)

    slots = repo.get_available_by_doctor(
        "unknown-doctor"
    )

    assert slots == []