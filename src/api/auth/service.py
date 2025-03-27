import jwt
import random
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from passlib.context import CryptContext
from src.core.database import get_session
from src.api.user.models import (
    Doctor,
    GenderEnum,
    Nurse,
    Patient,
    User,
    UserRole,
)
from src import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, session: Session = Depends(get_session)) -> None:
        self.session = session

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta
            or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

    def register(
        self,
        full_name: str,
        email: str,
        password: str,
        identification_number: str,
        **kwargs,
    ) -> User:
        try:
            statement_email = select(User).where(User.email == email)
            statement_id = select(User).where(
                User.username == identification_number
            )
            existing_email = self.session.exec(statement_email).one_or_none()
            existing_id = self.session.exec(statement_id).one_or_none()
            if existing_email or existing_id:
                raise HTTPException(
                    status_code=400, detail="Email or id already registered"
                )

            # Determine the role based on the identification number
            if "doc" in identification_number.lower():
                role = UserRole.doctor
            elif "nsc" in identification_number.lower():
                role = UserRole.nurse
            else:
                role = UserRole.patient

            # Create the user
            user = User(
                username=identification_number,
                email=email,
                hash=self.hash_password(password),
                role=role,
            )
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)

            # Create the appropriate role model based on the determined role
            if role == UserRole.doctor:
                doctor = Doctor(
                    user_id=user.id,
                    full_name=full_name,
                )
                self.session.add(doctor)
            elif role == UserRole.nurse:
                nurse = Nurse(user_id=user.id, full_name=full_name)
                self.session.add(nurse)
            else:
                # Create patient as default
                patient = Patient(
                    user_id=user.id,
                    full_name=full_name,
                    age=kwargs.get("age", 0),
                    gender=kwargs.get("gender", GenderEnum.OTHER),
                    current_weight_kg=kwargs.get("weight", 0.0),
                    current_height_cm=kwargs.get("height", 0.0),
                    hospital_card_id=kwargs.get(
                        "hospital_card_id", f"P-{user.id}"
                    ),
                )
                self.session.add(patient)

            self.session.commit()
            return user
        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred during registration: {str(e)}",
            )

    def login(self, email: str, password: str) -> tuple:
        statement = select(User).where(User.email == email.lower())
        user = self.session.exec(statement).one_or_none()
        if not user or not self.verify_password(password, user.hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = self.create_access_token({"sub": str(user.id)})

        # Load the associated entity based on the user's role
        if user.role == UserRole.doctor:
            statement = select(Doctor).where(Doctor.user_id == user.id)
            doctor = self.session.exec(statement).one()
            user.doctor = doctor
        elif user.role == UserRole.nurse:
            statement = select(Nurse).where(Nurse.user_id == user.id)
            nurse = self.session.exec(statement).one()
            user.nurse = nurse
        elif user.role == UserRole.patient:
            statement = select(Patient).where(Patient.user_id == user.id)
            patient = self.session.exec(statement).one()
            user.patient = patient

        return user, token

    def forgot_password(self, email: str) -> str:
        statement = select(User).where(User.email == email)
        user = self.session.exec(statement).one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        otp = f"{random.randint(100000, 999999)}"
        user.otp = otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        self.session.add(user)
        self.session.commit()
        return otp

    def confirm_otp(self, email: str, otp: str) -> bool:
        statement = select(User).where(User.email == email)
        user = self.session.exec(statement).one_or_none()
        if (
            not user
            or user.otp != otp
            or (user.otp_expiry and user.otp_expiry < datetime.utcnow())
        ):
            raise HTTPException(
                status_code=400, detail="Invalid or expired OTP"
            )
        token = self.create_access_token({"sub": str(user.id)})
        return token

    def reset_password(self, email: str, otp: str, new_password: str) -> User:
        statement = select(User).where(User.email == email)
        user = self.session.exec(statement).one_or_none()
        user.hash = self.hash_password(new_password)
        # Clear OTP fields
        user.otp = None
        user.otp_expiry = None
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
