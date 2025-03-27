from pydantic import BaseModel, EmailStr
from uuid import UUID


class RegisterInput(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    id_number: str  # Added field for role determination
    # For patient-specific fields
    age: int = None
    gender: str = None
    weight: float = None
    height: float = None
    hospital_card_id: str = None


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class DoctorResponse(BaseModel):
    id: UUID
    full_name: str


class NurseResponse(BaseModel):
    id: UUID
    full_name: str


class PatientResponse(BaseModel):
    id: UUID
    full_name: str
    age: int
    gender: str
    hospital_card_id: str
    current_weight_kg: float
    current_height_cm: float


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    doctor: DoctorResponse = None
    nurse: NurseResponse = None
    patient: PatientResponse = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ForgotPasswordInput(BaseModel):
    email: EmailStr


class ConfirmOtpInput(BaseModel):
    email: EmailStr
    otp: str


class ResetPasswordInput(BaseModel):
    email: EmailStr
    new_password: str


class EmailSchema(BaseModel):
    email: list[EmailStr]  # List of recipients
    subject: str
    body: str
