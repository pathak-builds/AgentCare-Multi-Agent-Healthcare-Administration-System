from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .slot import SlotOut
from .user import UserOut

class AppointmentCreate(BaseModel):
    slot_id: str
    reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentReschedule(BaseModel):
    new_slot_id: str

class AppointmentCancel(BaseModel):
    reason: Optional[str] = None

class AppointmentOut(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    slot_id: str
    status: str
    reason: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    slot: SlotOut
    # doctor and patient can be included if needed; for now minimal

    class Config:
        from_attributes = True