from pydantic import BaseModel

from src.api.appointment.model import UrgencyLevel


class AppointmentInput(BaseModel):
    appointment_date: str
    appointment_time: str
    status: str = "PENDING"


class EmergencyInput(BaseModel):
    status: str = "PENDING"
    description: str
    location: str
    urgency_level: UrgencyLevel
