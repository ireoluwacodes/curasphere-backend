from datetime import datetime
import uuid
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING, Optional
from src.api.base_model import ModelBase
from src.api.ehr.model import EHR
from src.api.uni_enum import BaseEnum

if TYPE_CHECKING:
    from src.api.user import Doctor, Patient


class UrgencyLevel(BaseEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AppointmentType(BaseEnum):
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"


class Appointment(ModelBase, SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    patient_id: uuid.UUID = Field(foreign_key="patient.id")
    doctor_id: uuid.UUID = Field(foreign_key="doctor.id", nullable=True)
    scheduled_time: datetime = Field(index=True)
    duration_minutes: int = Field(default=20)
    status: str = Field(default="pending")
    urgency_level: UrgencyLevel = Field(default=UrgencyLevel.LOW)
    type: AppointmentType = Field(default=AppointmentType.CONSULTATION)
    location: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)

    patient: "Patient" = Relationship(back_populates="appointments")
    ehr: "EHR" = Relationship(back_populates="appointment")
    doctor: "Doctor" = Relationship(back_populates="appointments")
