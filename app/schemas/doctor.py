from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .user import UserOut

class DoctorBase(BaseModel):
    specialization: Optional[str] = None
    license_number: Optional[str] = None

class DoctorCreate(DoctorBase):
    user_email: str = Field(..., description="Email of existing user (role staff)")
    department_id: str

class DoctorUpdate(BaseModel):
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    department_id: Optional[str] = None

class DoctorOut(DoctorBase):
    id: str
    department_id: str
    user: UserOut
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True