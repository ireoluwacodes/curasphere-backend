from typing import TYPE_CHECKING, Optional
from uuid import UUID
from sqlmodel import Field, Relationship, SQLModel

from src.api.base_model import ModelBase

if TYPE_CHECKING:
    from src.api.user import Patient, Doctor, Nurse
    from src.api.appointment.model import Appointment


class EHR(ModelBase, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: UUID = Field(foreign_key="patient.id")
    doctor_id: Optional[UUID] = Field(foreign_key="doctor.id", nullable=True)
    nurse_id: Optional[UUID] = Field(foreign_key="nurse.id", nullable=True)
    appointment_id: UUID = Field(foreign_key="appointment.id")

    # Vital signs recorded by nurse
    temperature: Optional[float] = None  # in Celsius
    blood_pressure: Optional[str] = None  # format: "120/80"
    heart_rate: Optional[int] = None  # in BPM

    # Doctor's input
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None
    further_tests: Optional[str] = None
    status: str = Field(
        default="initiated"
    )  # initiated, vitals_recorded, diagnosed, completed

    patient: "Patient" = Relationship(back_populates="ehr")
    doctor: Optional["Doctor"] = Relationship(back_populates="ehr")
    nurse: Optional["Nurse"] = Relationship(back_populates="ehr")
    appointment: "Appointment" = Relationship(back_populates="ehr")
