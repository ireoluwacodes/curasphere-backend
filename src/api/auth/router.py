from fastapi import APIRouter, BackgroundTasks, Depends
from src.api.auth.schemas import (
    RegisterInput,
    LoginInput,
    AuthResponse,
    ForgotPasswordInput,
    ConfirmOtpInput,
    ResetPasswordInput,
)
from src.api.auth.service import AuthService
from src import api

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
    input: ForgotPasswordInput,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(),
):
    otp = auth_service.forgot_password(input.email)
    my_email = api.EmailSchema(
        subject="Forgot Password",
        email=[input.email],
        body=f"<h2>Hello, your otp to reset password is {otp}!</h2>",
    )
    background_tasks.add_task(auth_service.send_email, my_email)
    return {"message": "Email sent"}


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
