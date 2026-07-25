from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AuditEventOut(BaseModel):
    id: str
    user_id: Optional[str]
    event_type: str
    description: str
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True