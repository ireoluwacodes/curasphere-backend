from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class VitalSignsInput(BaseModel):
    temperature: float
    blood_pressure: str
    heart_rate: int


class DiagnosisInput(BaseModel):
    diagnosis: str
    prescription: Optional[str] = None
    further_tests: Optional[str] = None


class EHROutput(BaseModel):
    id: int
    patient_id: UUID
    doctor_id: Optional[UUID]
    nurse_id: Optional[UUID]
    appointment_id: UUID
    temperature: Optional[float]
    blood_pressure: Optional[str]
    heart_rate: Optional[int]
    diagnosis: Optional[str]
    prescription: Optional[str]
    further_tests: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
