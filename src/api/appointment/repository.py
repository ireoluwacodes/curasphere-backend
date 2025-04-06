from fastapi import Depends
from sqlmodel import Session, select
from datetime import datetime, date
from sqlalchemy import func

from src.api.appointment.model import (
    Appointment,
    AppointmentType,
)
from src.api.user.models import Patient
from src.core.database import get_session
from sqlalchemy.orm import selectinload


class AppointmentRepository:
    def __init__(self, session: Session = Depends(get_session)) -> None:
        self.session = session

    def create(self, patient_id, data):
        # Parse date and time
        date_str = data.appointment_date
        time_str = data.appointment_time
        scheduled_time = datetime.strptime(
            f"{date_str} {time_str}", "%Y-%m-%d %H:%M"
        )

        appointment = Appointment(
            patient_id=patient_id,
            scheduled_time=scheduled_time,
            status=data.status,
            type=AppointmentType.CONSULTATION,
        )
        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(appointment)
        return appointment

    def create_emergency(self, patient_id, data):
        appointment = Appointment(
            patient_id=patient_id,
            scheduled_time=datetime.now(),
            status=data.status,
            type=AppointmentType.EMERGENCY,
            urgency_level=data.urgency_level,
            location=data.location,
            description=data.description,
        )
        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(appointment)
        return appointment

    def get(self, user_id, appointment_id):
        statement = select(Appointment).where(
            (Appointment.id == appointment_id)
            & (
                (Appointment.patient_id == user_id)
                | (Appointment.doctor_id == user_id)
            )
        )
        return self.session.exec(statement).one_or_none()

    def list(self, user_id):
        statement = (
            select(Appointment)
            .where(
                (Appointment.patient_id == user_id)
                | (Appointment.doctor_id == user_id)
            )
            .options(selectinload(Appointment.patient))
        )
        appointments = self.session.exec(statement).all()

        enriched_appointments = []
        for appointment in appointments:
            patient = self.session.exec(
                select(Patient).where(Patient.id == appointment.patient_id)
            ).one()
            if patient:
                new = {}
                new["appointment"] = appointment
                new["patient"] = patient
                enriched_appointments.append(new)
        return enriched_appointments

    def nurse_list_all(self):
        today = date.today()
        statement = select(Appointment).where(
            (func.date(Appointment.scheduled_time) == today)
            | (
                (func.date(Appointment.scheduled_time) < today)
                & (Appointment.status != "COMPLETED")
            )
        )
        appointments = self.session.exec(statement).all()

        enriched_appointments = []
        for appointment in appointments:
            patient = self.session.exec(
                select(Patient).where(Patient.id == appointment.patient_id)
            ).one()
            if patient:
                new = {}
                new["appointment"] = appointment
                new["patient"] = patient
                enriched_appointments.append(new)
        return enriched_appointments

    def update(self, user_id, appointment_id, data):
        appointment = self.get(user_id, appointment_id)
        if appointment:
            # Update the fields
            if hasattr(data, "appointment_date") and hasattr(
                data, "appointment_time"
            ):
                date_str = data.appointment_date
                time_str = data.appointment_time
                appointment.scheduled_time = datetime.strptime(
                    f"{date_str} {time_str}", "%Y-%m-%d %H:%M"
                )

            if hasattr(data, "status"):
                appointment.status = data.status

            self.session.add(appointment)
            self.session.commit()
            self.session.refresh(appointment)
        return appointment

    def delete(self, user_id, appointment_id):
        appointment = self.get(user_id, appointment_id)
        if appointment:
            self.session.delete(appointment)
            self.session.commit()
        return {"success": True}
