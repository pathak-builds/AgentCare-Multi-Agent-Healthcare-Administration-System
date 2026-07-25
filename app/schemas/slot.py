from pydantic import BaseModel
from datetime import datetime

class SlotCreate(BaseModel):
    doctor_id: str
    department_id: str
    start_time: datetime
    end_time: datetime

class SlotOut(BaseModel):
    id: str
    doctor_id: str
    department_id: str
    start_time: datetime
    end_time: datetime
    is_booked: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True