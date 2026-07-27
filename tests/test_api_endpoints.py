"""
Integration tests for FastAPI endpoints.
"""

import pytest


# ---------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------

def test_health(client):

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------

def test_register(client):

    response = client.post(
        "/auth/register",
        json={
            "email": "new@test.com",
            "password": "new123456",
            "full_name": "New User",
            "role": "patient",
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert "access_token" in data
    assert data["access_token"]


# ---------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------

def test_login(client):

    client.post(
        "/auth/register",
        json={
            "email": "login@test.com",
            "password": "password123",
            "full_name": "Login User",
            "role": "patient",
        },
    )

    response = client.post(
    "/auth/login",
    data={
        "username": "login@test.com",
        "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data


# ---------------------------------------------------------------------
# Current User
# ---------------------------------------------------------------------

def test_current_user(client, patient_token):

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {patient_token}",
        },
    )

    assert response.status_code == 200

    user = response.json()

    assert user["role"] == "patient"


# ---------------------------------------------------------------------
# RBAC
# ---------------------------------------------------------------------

def test_patient_cannot_create_department(
    client,
    patient_token,
):

    response = client.post(
        "/departments/",
        json={
            "name": "Test Department",
        },
        headers={
            "Authorization": f"Bearer {patient_token}",
        },
    )

    assert response.status_code == 403


# ---------------------------------------------------------------------
# Available Slots
# ---------------------------------------------------------------------

def test_available_slots(
    client,
    patient_token,
    seed_data,
):

    doctor_id = seed_data["doctor"].id

    response = client.get(
        f"/slots/available/{doctor_id}",
        headers={
            "Authorization": f"Bearer {patient_token}",
        },
    )

    assert response.status_code == 200

    slots = response.json()

    assert len(slots) == 1


# ---------------------------------------------------------------------
# Appointment Booking
# ---------------------------------------------------------------------

def test_book_appointment(
    client,
    patient_token,
    seed_data,
):

    response = client.post(
        "/appointments/",
        json={
            "slot_id": seed_data["slot"].id,
            "reason": "Routine checkup",
            "notes": "",
        },
        headers={
            "Authorization": f"Bearer {patient_token}",
        },
    )

    assert response.status_code in (200, 201)

    appointment = response.json()

    assert appointment["status"] == "scheduled"


# ---------------------------------------------------------------------
# Document Upload
# ---------------------------------------------------------------------

def test_document_upload(
    client,
    patient_token,
):

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "report.pdf",
                b"Fake PDF content",
                "application/pdf",
            )
        },
        headers={
            "Authorization": f"Bearer {patient_token}",
        },
    )

    assert response.status_code in (200, 201)

    document = response.json()

    assert document["original_filename"] == "report.pdf"


# ---------------------------------------------------------------------
# Unauthorized Access
# ---------------------------------------------------------------------

def test_protected_endpoint_requires_auth(client):

    response = client.get("/users/me")

    assert response.status_code in (401, 403)


# ---------------------------------------------------------------------
# Invalid Login
# ---------------------------------------------------------------------

def test_invalid_login(client):

    response = client.post(
    "/auth/login",
    data={
        "username": "wrong@test.com",
        "password": "wrongpassword",
        },
    )

    assert response.status_code in (400, 401)


# ---------------------------------------------------------------------
# Invalid Slot Booking
# ---------------------------------------------------------------------

def test_invalid_slot_booking(
    client,
    patient_token,
):

    response = client.post(
        "/appointments/",
        json={
            "slot_id": "invalid-slot-id",
            "reason": "Test",
            "notes": "",
        },
        headers={
            "Authorization": f"Bearer {patient_token}",
        },
    )

    assert response.status_code in (400, 404)


# ---------------------------------------------------------------------
# Workflow API
# ---------------------------------------------------------------------

def test_start_workflow(
    client,
    patient_token,
):

    response = client.post(
        "/workflow/start",
        json={
            "intent": "Book a cardiology appointment",
        },
        headers={
            "Authorization": f"Bearer {patient_token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["workflow_status"] == "completed"
    assert "final_state" in data