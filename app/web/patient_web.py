from fastapi import (
    APIRouter,
    Request,
    Form,
    Depends,
    HTTPException,
    UploadFile,
    File,
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import json

from app.database.session import get_db
from app.services.appointment_service import AppointmentService
from app.services.document_service import DocumentService
from app.services.workflow_service import WorkflowService

from app.repositories.patient_repository import PatientRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.document_repository import DocumentRepository

from app.models.workflow import WorkflowRun
from app.web.deps import require_role_web


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

patient_only = require_role_web("patient")


def get_patient_id(user, db):
    repo = PatientRepository(db)

    patient = repo.get_by_user_id(user.id)

    if not patient:
        raise HTTPException(
            status_code=400,
            detail="Patient profile not found",
        )

    return patient.id


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

@router.get("/dashboard")
def patient_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(patient_only),
):
    patient_id = get_patient_id(current_user, db)

    appointments = AppointmentRepository(db).get_by_patient(patient_id)

    documents = DocumentRepository(db).get_by_patient(patient_id)

    workflows = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.patient_id == patient_id)
        .order_by(WorkflowRun.created_at.desc())
        .limit(5)
        .all()
    )

    return templates.TemplateResponse(
        "patient/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "appointments": appointments,
            "documents": documents,
            "workflows": workflows,
        },
    )


# ---------------------------------------------------------
# Appointment Booking
# ---------------------------------------------------------

@router.get("/book-appointment")
def book_appointment_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(patient_only),
):
    departments = DepartmentRepository(db).get_all()

    return templates.TemplateResponse(
        "patient/book_appointment.html",
        {
            "request": request,
            "user": current_user,
            "departments": departments,
        },
    )


@router.post("/book-appointment")
async def book_appointment_submit(
    request: Request,
    slot_id: str = Form(...),
    reason: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user=Depends(patient_only),
):
    patient_id = get_patient_id(current_user, db)

    service = AppointmentService(db)

    try:
        service.book_appointment(
            patient_id,
            slot_id,
            reason,
            notes,
            current_user.id,
        )

    except Exception as e:

        return templates.TemplateResponse(
            "patient/book_appointment.html",
            {
                "request": request,
                "user": current_user,
                "departments": DepartmentRepository(db).get_all(),
                "error": str(e),
            },
        )

    return RedirectResponse(
        "/patient/appointments",
        status_code=303,
    )


# ---------------------------------------------------------
# Appointments
# ---------------------------------------------------------

@router.get("/appointments")
def my_appointments(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(patient_only),
):
    appointments = AppointmentService(
        db
    ).get_patient_appointments_by_user_id(current_user.id)

    return templates.TemplateResponse(
        "patient/appointments.html",
        {
            "request": request,
            "user": current_user,
            "appointments": appointments,
        },
    )


@router.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(patient_only),
):
    AppointmentService(db).cancel_appointment(
        appointment_id,
        current_user.id,
    )

    return RedirectResponse(
        "/patient/appointments",
        status_code=303,
    )


# ---------------------------------------------------------
# Documents
# ---------------------------------------------------------

@router.get("/documents")
def my_documents(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(patient_only),
):
    patient_id = get_patient_id(current_user, db)

    documents = DocumentRepository(db).get_by_patient(patient_id)

    return templates.TemplateResponse(
        "patient/documents.html",
        {
            "request": request,
            "user": current_user,
            "documents": documents,
        },
    )


@router.post("/documents/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(patient_only),
):
    try:
        await DocumentService(db).upload_document(
            current_user.id,
            file,
        )

    except Exception as e:

        return templates.TemplateResponse(
            "patient/documents.html",
            {
                "request": request,
                "user": current_user,
                "error": str(e),
            },
        )

    return RedirectResponse(
        "/patient/documents",
        status_code=303,
    )


# ---------------------------------------------------------
# Workflow List
# ---------------------------------------------------------

@router.get("/workflows")
def my_workflows(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(patient_only),
):
    patient_id = get_patient_id(current_user, db)

    workflows = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.patient_id == patient_id)
        .order_by(WorkflowRun.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        "patient/workflows.html",
        {
            "request": request,
            "user": current_user,
            "workflows": workflows,
        },
    )


# ---------------------------------------------------------
# Workflow Detail
# ---------------------------------------------------------

@router.get("/workflows/{workflow_id}")
def workflow_detail(
    workflow_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(patient_only),
):
    workflow = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.id == workflow_id)
        .first()
    )

    if workflow is None:
        raise HTTPException(status_code=404)

    state = {}

    if workflow.state_snapshot:

        try:
            state = json.loads(workflow.state_snapshot)

        except Exception as e:

            print("Failed to parse workflow JSON:", e)

            state = {}

    return templates.TemplateResponse(
        "patient/workflow_detail.html",
        {
            "request": request,
            "user": current_user,
            "workflow": workflow,
            "state": state,
        },
    )


# ---------------------------------------------------------
# Start Workflow
# ---------------------------------------------------------

@router.post("/workflows/start")
def start_workflow_from_web(
    intent: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(patient_only),
):
    WorkflowService(db).start_workflow(
        current_user.id,
        intent,
    )

    return RedirectResponse(
        "/patient/workflows",
        status_code=303,
    )