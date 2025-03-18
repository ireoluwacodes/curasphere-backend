from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

from src.api.base_model import ModelBase

if TYPE_CHECKING:
    from src.api.user import Patient


class EHR(ModelBase, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.id")
    doctor_id: int = Field(foreign_key="doctor.id")
    nurse_id: Optional[int] = Field(foreign_key="nurse.id", nullable=True)
    diagnosis: str
    prescription: Optional[str] = None

    patient: "Patient" = Relationship(back_populates="ehr")
