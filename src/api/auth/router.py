from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.api.auth.schemas import (
    RegisterInput,
    AuthResponse,
    ForgotPasswordInput,
    ConfirmOtpInput,
    ResetPasswordInput,
    UserResponse,
    DoctorResponse,
    NurseResponse,
    PatientResponse,
)
from src.api.auth.service import AuthService
from src import api
from src.api.deps import get_current_user
from src.api.user.models import User, UserRole

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(input: RegisterInput, auth_service: AuthService = Depends()):
    kwargs = {}

    kwargs["age"] = input.age
    kwargs["gender"] = input.gender
    kwargs["weight"] = input.weight
    kwargs["height"] = input.height
    kwargs["hospital_card_id"] = input.hospital_card_id

    user = auth_service.register(
        input.full_name,
        input.email,
        input.password,
        input.id_number,
        **kwargs,
    )
    return UserResponse(
        id=user.id, username=user.username, email=user.email, role=user.role
    )


@router.post("/login", response_model=AuthResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(),
):
    user, token = auth_service.login(form_data.username, form_data.password)

    user_response = UserResponse(
        id=user.id, username=user.username, email=user.email, role=user.role
    )

    # Create the appropriate entity response based on user's role
    if user.role == UserRole.doctor and user.doctor:
        auth_service.set_doctor_as_active(user.id)
        user_response.doctor = DoctorResponse(
            id=user.doctor.id, full_name=user.doctor.full_name
        )
    elif user.role == UserRole.nurse and user.nurse:
        user_response.nurse = NurseResponse(
            id=user.nurse.id, full_name=user.nurse.full_name
        )
    elif user.role == UserRole.patient and user.patient:
        user_response.patient = PatientResponse(
            id=user.patient.id,
            full_name=user.patient.full_name,
            age=user.patient.age,
            gender=user.patient.gender,
            hospital_card_id=user.patient.hospital_card_id,
            current_weight_kg=user.patient.current_weight_kg,
            current_height_cm=user.patient.current_height_cm,
        )

    return AuthResponse(access_token=token, user=user_response)


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
    token = auth_service.confirm_otp(input.email, input.otp)
    return {"detail": "OTP confirmed", token: token}


@router.post("/reset-password")
def reset_password(
    input: ResetPasswordInput,
    auth_service: AuthService = Depends(),
    user: User = Depends(get_current_user),
):
    auth_service.reset_password(input.email, input.new_password)
    return {"detail": "Password reset successfully"}
