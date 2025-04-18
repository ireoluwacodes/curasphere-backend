from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.api.auth.schemas import (
    DoctorResponse,
    NurseResponse,
    PatientResponse,
)


class VitalSignsInput(BaseModel):
    temperature: float
    blood_pressure: str
    heart_rate: int


class DiagnosisInput(BaseModel):
    diagnosis: str
    prescription: str


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

    class Config:
        from_attributes = True


# Nested patient schema
class EntityResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str

    class Config:
        from_attributes = True


# Appointment schema
class AppointmentResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    patient_id: UUID
    doctor_id: Optional[UUID]
    scheduled_time: datetime
    duration_minutes: int
    status: str
    urgency_level: str
    type: str
    location: Optional[str]
    description: Optional[str]
    doctor: Optional[EntityResponse]  # doctor might be optional
    patient: Optional[EntityResponse]
    ehr: Optional[EHROutput]

    class Config:
        from_attributes = True


# List response
class AppointmentListResponse(BaseModel):
    records: List[AppointmentResponse]


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    doctor: Optional[DoctorResponse]
    nurse: Optional[NurseResponse]
    patient: Optional[PatientResponse]


class PatientResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    age: int
    hospital_card_id: str
    gender: str
    current_weight_kg: float
    current_height_cm: float
    user: UserResponse
    appointments: List[AppointmentResponse]
    ehr: List[EHROutput]


class PatientRecordResponse(BaseModel):
    record: PatientResponse
