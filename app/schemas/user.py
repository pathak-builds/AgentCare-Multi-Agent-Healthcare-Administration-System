from pydantic import BaseModel
from datetime import datetime

class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True