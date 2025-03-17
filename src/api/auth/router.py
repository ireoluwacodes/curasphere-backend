from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.api.auth.schemas import (
    RegisterInput,
    AuthResponse,
    ForgotPasswordInput,
    ConfirmOtpInput,
    ResetPasswordInput,
)
from src.api.auth.service import AuthService
from src import api
from src.api.deps import get_current_user
from src.api.user.models import User

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
def register(input: RegisterInput, auth_service: AuthService = Depends()):
    user = auth_service.register(input.username, input.email, input.password)
    token = auth_service.create_access_token({"sub": str(user.id)})
    return AuthResponse(access_token=token)


@router.post("/login", response_model=AuthResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(),
):
    token = auth_service.login(form_data.username, form_data.password)
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
    input: ResetPasswordInput,
    auth_service: AuthService = Depends(),
    user: User = Depends(get_current_user),
):
    auth_service.reset_password(input.email, input.otp, input.new_password)
    return {"detail": "Password reset successfully"}
