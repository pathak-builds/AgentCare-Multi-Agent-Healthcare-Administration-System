# """
# Import all models so Alembic can detect them.
# """
from .base import Base
from .user import User, RoleEnum
from .patient import PatientProfile
from .department import Department
from .doctor import Doctor
from .slot import AppointmentSlot
from .appointment import Appointment
from .document import PatientDocument
from .workflow import WorkflowRun
from .reminder import Reminder
from .escalation import Escalation
from .audit import AuditEvent

