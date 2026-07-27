from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.web.deps import require_role_web
from app.services.department_service import DepartmentService
from app.services.doctor_service import DoctorService
from app.services.slot_service import SlotService
from app.repositories.department_repository import DepartmentRepository
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.slot_repository import SlotRepository
from app.repositories.audit_repository import AuditRepository
from app.models.escalation import Escalation, EscalationStatus
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
admin_only = require_role_web("admin")
staff_or_admin = require_role_web("admin", "hospital_staff")

@router.get("/dashboard")
def admin_dashboard(request: Request, current_user = Depends(admin_only)):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

# Departments
@router.get("/departments")
def manage_departments(request: Request, db: Session = Depends(get_db), current_user = Depends(admin_only)):
    dept_repo = DepartmentRepository(db)
    departments = dept_repo.get_all()
    return templates.TemplateResponse("admin/departments.html", {"request": request, "departments": departments})

@router.post("/departments/create")
def create_department(
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    current_user = Depends(admin_only)
):
    service = DepartmentService(db)
    service.create_department(name, description, current_user.id)
    return RedirectResponse("/admin/departments", status_code=303)

@router.post("/departments/{dept_id}/delete")
def delete_department(dept_id: str, db: Session = Depends(get_db), current_user = Depends(admin_only)):
    service = DepartmentService(db)
    service.delete_department(dept_id, current_user.id)
    return RedirectResponse("/admin/departments", status_code=303)

# Doctors
@router.get("/doctors")
def manage_doctors(request: Request, db: Session = Depends(get_db), current_user = Depends(admin_only)):
    doctor_repo = DoctorRepository(db)
    doctors = doctor_repo.get_all()
    dept_repo = DepartmentRepository(db)
    departments = dept_repo.get_all()
    return templates.TemplateResponse("admin/doctors.html", {"request": request, "doctors": doctors, "departments": departments})

@router.post("/doctors/create")
def create_doctor(
    user_email: str = Form(...),
    department_id: str = Form(...),
    specialization: str = Form(""),
    license_number: str = Form(""),
    db: Session = Depends(get_db),
    current_user = Depends(admin_only)
):
    service = DoctorService(db)
    try:
        service.create_doctor(user_email, department_id, specialization, license_number, current_user.id)
    except Exception as e:
        # Redirect with error (simplified – pass via query param, but we'll just redirect)
        pass
    return RedirectResponse("/admin/doctors", status_code=303)

# Slots
@router.get("/slots")
def manage_slots(request: Request, db: Session = Depends(get_db), current_user = Depends(staff_or_admin)):
    slot_repo = SlotRepository(db)
    slots = slot_repo.get_all()
    doctor_repo = DoctorRepository(db)
    doctors = doctor_repo.get_all()
    dept_repo = DepartmentRepository(db)
    departments = dept_repo.get_all()
    return templates.TemplateResponse("admin/slots.html", {"request": request, "slots": slots, "doctors": doctors, "departments": departments})

@router.post("/slots/create")
def create_slot(
    doctor_id: str = Form(...),
    department_id: str = Form(...),
    start_time: str = Form(...),   # datetime-local input
    end_time: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(staff_or_admin)
):
    service = SlotService(db)
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        service.create_slot(doctor_id, department_id, start, end, current_user.id)
    except Exception:
        pass
    return RedirectResponse("/admin/slots", status_code=303)

@router.post("/slots/{slot_id}/delete")
def delete_slot(slot_id: str, db: Session = Depends(get_db), current_user = Depends(admin_only)):
    service = SlotService(db)
    service.delete_slot(slot_id, current_user.id)
    return RedirectResponse("/admin/slots", status_code=303)

# Escalations
@router.get("/escalations")
def view_escalations(request: Request, db: Session = Depends(get_db), current_user = Depends(admin_only)):
    escalations = db.query(Escalation).order_by(Escalation.created_at.desc()).all()
    return templates.TemplateResponse("admin/escalations.html", {"request": request, "escalations": escalations})

@router.post("/escalations/{esc_id}/approve")
def approve_escalation(esc_id: str, db: Session = Depends(get_db), current_user = Depends(admin_only)):
    esc = db.query(Escalation).filter(Escalation.id == esc_id).first()
    if esc:
        esc.status = EscalationStatus.APPROVED
        esc.reviewer_id = current_user.id
        esc.decision_notes = "Approved"
        db.commit()
    return RedirectResponse("/admin/escalations", status_code=303)

@router.post("/escalations/{esc_id}/reject")
def reject_escalation(esc_id: str, db: Session = Depends(get_db), current_user = Depends(admin_only)):
    esc = db.query(Escalation).filter(Escalation.id == esc_id).first()
    if esc:
        esc.status = EscalationStatus.REJECTED
        esc.reviewer_id = current_user.id
        esc.decision_notes = "Rejected"
        db.commit()
    return RedirectResponse("/admin/escalations", status_code=303)

# Audit logs
@router.get("/audit")
def audit_logs(request: Request, db: Session = Depends(get_db), current_user = Depends(admin_only)):
    repo = AuditRepository(db)
    logs = repo.get_all(limit=200)
    return templates.TemplateResponse("admin/audit.html", {"request": request, "logs": logs})