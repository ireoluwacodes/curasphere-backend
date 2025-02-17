from fastapi import APIRouter, Depends
from src.api.auth.schemas import (
    RegisterInput,
    LoginInput,
    AuthResponse,
    ForgotPasswordInput,
    ConfirmOtpInput,
    ResetPasswordInput,
)
from src.api.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
def register(input: RegisterInput, auth_service: AuthService = Depends()):
    user = auth_service.register(input.username, input.email, input.password)
    token = auth_service.create_access_token({"sub": str(user.id)})
    return AuthResponse(access_token=token)


@router.post("/login", response_model=AuthResponse)
def login(input: LoginInput, auth_service: AuthService = Depends()):
    token = auth_service.login(input.email, input.password)
    return AuthResponse(access_token=token)


@router.post("/forgot-password")
def forgot_password(
    input: ForgotPasswordInput, auth_service: AuthService = Depends()
):
    otp = auth_service.forgot_password(input.email)
    return {
        "detail": "OTP sent to your email",
        "otp": otp,
    }  # Remove otp in production


@router.post("/confirm-otp")
def confirm_otp(
    input: ConfirmOtpInput, auth_service: AuthService = Depends()
):
    auth_service.confirm_otp(input.email, input.otp)
    return {"detail": "OTP confirmed"}


@router.post("/reset-password")
def reset_password(
    input: ResetPasswordInput, auth_service: AuthService = Depends()
):
    auth_service.reset_password(input.email, input.otp, input.new_password)
    return {"detail": "Password reset successfully"}
