from pydantic import BaseModel

from src.api.appointment.model import UrgencyLevel


class AppointmentInput(BaseModel):
    appointment_date: str
    appointment_time: str
    status: str = "pending"


class EmergencyInput(BaseModel):
    status: str = "pending"
    description: str
    location: str
    urgency_level: UrgencyLevel
