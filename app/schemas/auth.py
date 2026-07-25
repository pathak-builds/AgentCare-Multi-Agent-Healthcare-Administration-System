"""
Pydantic schemas for authentication requests and responses.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.user import RoleEnum

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(default=RoleEnum.PATIENT.value)  # only "patient" allowed

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v != RoleEnum.PATIENT.value:
            raise ValueError("Only 'patient' registration is supported")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict  # simplified for now; could be a UserOut model later