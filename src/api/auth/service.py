from fastapi_mail import FastMail, MessageSchema, MessageType
import jwt
import random
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from passlib.context import CryptContext
from src.core.database import get_session
from src.api.user.models import User
from src import settings
from src import core
from src import api

# Dependency install: pip install passlib pyjwt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, session: Session = Depends(get_session)) -> None:
        self.session = session

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    async def send_email(email: api.EmailSchema):
        message = MessageSchema(
            subject=email.subject,
            recipients=email.model_dump().get("email"),
            body=email.body,
            subtype=MessageType.html,  # You can also use "plain" for text emails
        )

        fm = FastMail(core.conf)
        await fm.send_message(message)

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

    def register(self, username: str, email: str, password: str) -> User:
        statement = select(User).where(User.email == email)
        existing_user = self.session.exec(statement).one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Email already registered"
            )
        user = User(
            username=username,
            email=email,
            password=self.hash_password(password),
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def login(self, email: str, password: str) -> str:
        statement = select(User).where(User.email == email)
        user = self.session.exec(statement).one_or_none()
        if not user or not self.verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = self.create_access_token({"sub": str(user.id)})
        return token

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
        return True

    def reset_password(self, email: str, otp: str, new_password: str) -> User:
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
        user.password = self.hash_password(new_password)
        # Clear OTP fields
        user.otp = None
        user.otp_expiry = None
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
