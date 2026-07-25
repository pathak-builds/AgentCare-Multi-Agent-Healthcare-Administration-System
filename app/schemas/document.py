from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentOut(BaseModel):
    id: str
    patient_id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    sha256_checksum: str
    classification: Optional[str]
    upload_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True