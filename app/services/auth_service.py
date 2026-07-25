"""
Authentication business logic: registration and login.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, RoleEnum
from app.models.patient import PatientProfile
from app.repositories.user_repository import UserRepository
from app.repositories.patient_repository import PatientRepository
from app.auth.jwt import hash_password, verify_password, create_access_token

class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.patient_repo = PatientRepository(db)

    def register(self, email: str, password: str, full_name: str, role: str = RoleEnum.PATIENT) -> dict:
        # Only patient registration via public endpoint
        if role != RoleEnum.PATIENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only patient registration is allowed here",
            )
        if self.user_repo.user_exists(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        # Create user
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=RoleEnum.PATIENT,
        )
        user = self.user_repo.create(user)
        # Create patient profile
        profile = PatientProfile(
            user_id=user.id,
        )
        self.patient_repo.create(profile)
        # Generate token
        token = create_access_token(str(user.id), user.role.value)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
            }
        }

    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        token = create_access_token(str(user.id), user.role.value)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
            }
        }