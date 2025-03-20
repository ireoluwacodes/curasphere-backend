from pydantic import BaseModel, EmailStr


class RegisterInput(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    identification_number: str  # Added field for role determination
    # For patient-specific fields
    age: int = None
    gender: str = None
    current_weight_kg: float = None
    current_height_cm: float = None
    hospital_card_id: str = None


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordInput(BaseModel):
    email: EmailStr


class ConfirmOtpInput(BaseModel):
    email: EmailStr
    otp: str


class ResetPasswordInput(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class EmailSchema(BaseModel):
    email: list[EmailStr]  # List of recipients
    subject: str
    body: str
