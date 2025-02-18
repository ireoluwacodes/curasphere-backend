from pydantic import BaseModel, EmailStr


class RegisterInput(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    password: str
    age: str
    weight_kg: str
    height_cm: str
    gender: str


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
