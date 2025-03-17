from datetime import datetime
import uuid
from typing import Optional, UUID
from sqlmodel import Field, SQLModel
from src.api.base_model import TimestampMixin
from src.api.uni_enum import BaseEnum


class UserRole(BaseEnum):
    admin = "admin"
    patient = "patient"
    doctor = "doctor"
    nurse = "nurse"


class User(TimestampMixin, SQLModel, table=True):
    id: Optional[UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    username: str
    email: str
    role: UserRole
    password: str
    otp: Optional[str] = Field(default=None, nullable=True)
    otp_expiry: Optional[datetime] = Field(default=None, nullable=True)
