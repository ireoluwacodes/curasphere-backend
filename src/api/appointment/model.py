from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING, Optional
from src.api.base_model import ModelBase

if TYPE_CHECKING:
    from src.api.user import Doctor, Patient


class Appointment(ModelBase, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.id")
    doctor_id: int = Field(foreign_key="doctor.id")
    scheduled_time: datetime
    status: str = Field(default="pending")

    patient: "Patient" = Relationship(back_populates="appointments")
    doctor: "Doctor" = Relationship(back_populates="appointments")
