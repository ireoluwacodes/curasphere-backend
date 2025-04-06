from datetime import datetime
import uuid
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from src.api.appointment.model import Appointment
from src.api.base_model import ModelBase
from src.api.ehr.model import EHR
from src.api.uni_enum import BaseEnum


class UserRole(BaseEnum):
    admin = "admin"
    patient = "patient"
    doctor = "doctor"
    nurse = "nurse"


class GenderEnum(BaseEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class User(ModelBase, SQLModel, table=True):
    __tablename__ = "users"  # Change table name from "user" to "users"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    username: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    role: UserRole = Field(default=UserRole.patient, nullable=False)
    hash: str
    otp: Optional[str] = Field(default=None, nullable=True)
    otp_expiry: Optional[datetime] = Field(default=None, nullable=True)

    doctor: Optional["Doctor"] = Relationship(back_populates="user")
    nurse: Optional["Nurse"] = Relationship(back_populates="user")
    patient: Optional["Patient"] = Relationship(back_populates="user")


class Doctor(ModelBase, SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True)
    full_name: str = Field(nullable=False)
    user: "User" = Relationship(back_populates="doctor")
    ehr: List["EHR"] = Relationship(back_populates="doctor")
    appointments: List["Appointment"] = Relationship(back_populates="doctor")


class Nurse(ModelBase, SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True)
    full_name: str = Field(nullable=False)

    user: "User" = Relationship(back_populates="nurse")
    ehr: List["EHR"] = Relationship(back_populates="nurse")


class Patient(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True)
    full_name: str = Field(nullable=False)
    age: int = Field(nullable=False)
    hospital_card_id: str
    gender: GenderEnum = Field(nullable=False)
    current_weight_kg: float = Field(nullable=False)
    current_height_cm: float = Field(nullable=False)

    user: "User" = Relationship(back_populates="patient")
    appointments: List["Appointment"] = Relationship(back_populates="patient")
    ehr: List["EHR"] = Relationship(back_populates="patient")
