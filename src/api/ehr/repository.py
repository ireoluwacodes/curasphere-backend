from fastapi import Depends
from sqlmodel import Session, select

from sqlalchemy.orm import selectinload
from typing import Optional, List
from uuid import UUID

from src.api.ehr.model import EHR
from src.api.appointment.model import Appointment
from src.api.user.models import Patient
from src.core.database import get_session


class EHRRepository:
    def __init__(self, session: Session = Depends(get_session)) -> None:
        self.session = session

    def assign_doctor(self, doctor_id: UUID, appointment_id: UUID) -> EHR:
        """Create a new EHR record for an appointment"""

        statement = select(EHR).where(EHR.appointment_id == appointment_id)
        ehr = self.session.exec(statement).one_or_none()
        statement = select(Appointment).where(
            Appointment.id == appointment_id
        )
        appointment = self.session.exec(statement).one_or_none()

        if not ehr or not appointment:
            raise ValueError("EHR or Appointment not found")
        ehr.doctor_id = doctor_id
        appointment.doctor_id = doctor_id
        self.session.add(ehr)
        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(ehr)
        return ehr

    def update_vitals(
        self, appointment_id: UUID, data, nurse_id: UUID
    ) -> Optional[EHR]:
        """Initialize EHR and Update vital signs"""
        # Get appointment to retrieve patient_id
        statement = select(Appointment).where(
            Appointment.id == appointment_id
        )
        appointment = self.session.exec(statement).one_or_none()

        if not appointment:
            raise ValueError(
                f"Appointment with ID {appointment_id} not found"
            )

        ehr = EHR(
            patient_id=appointment.patient_id,
            nurse_id=nurse_id,
            appointment_id=appointment_id,
            temperature=data.temperature,
            blood_pressure=data.blood_pressure,
            heart_rate=data.heart_rate,
            status="vitals_recorded",
        )

        appointment.status = "VITALS_RECORDED"
        self.session.add(appointment)
        self.session.add(ehr)
        self.session.commit()
        self.session.refresh(ehr)
        return ehr

    def update_diagnosis(
        self, appointment_id: UUID, doctor_id: UUID, data
    ) -> Optional[EHR]:
        """Update diagnosis and prescription by doctor"""
        statement = select(EHR).where(EHR.appointment_id == appointment_id)
        ehr = self.session.exec(statement).one_or_none()
        if not ehr or ehr.doctor_id != doctor_id:
            return None

        ehr.diagnosis = data.diagnosis
        ehr.prescription = data.prescription
        ehr.status = "diagnosed"

        statement = select(Appointment).where(
            Appointment.id == appointment_id
        )
        appointment = self.session.exec(statement).one_or_none()
        appointment.status = "DIAGNOSED"

        self.session.add(ehr)
        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(ehr)
        return ehr

    def complete_ehr(
        self, appointment_id: UUID, doctor_id: UUID
    ) -> Optional[EHR]:
        """Mark EHR as completed"""
        statement = select(EHR).where(EHR.appointment_id == appointment_id)
        ehr = self.session.exec(statement).one_or_none()
        if not ehr or ehr.doctor_id != doctor_id:
            return None

        ehr.status = "completed"
        statement = select(Appointment).where(
            Appointment.id == appointment_id
        )
        appointment = self.session.exec(statement).one_or_none()
        appointment.status = "COMPLETED"

        self.session.add(ehr)
        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(ehr)
        return ehr

    def get_by_id(self, ehr_id: int) -> Optional[EHR]:
        """Get EHR by ID"""
        statement = select(EHR).where(EHR.id == ehr_id)
        return self.session.exec(statement).one_or_none()

    def get_by_appointment(self, appointment_id: UUID) -> Optional[EHR]:
        """Get EHR by appointment ID"""
        statement = select(EHR).where(EHR.appointment_id == appointment_id)
        return self.session.exec(statement).one_or_none()

    def get_patient_records(self, appointment_id: UUID) -> Patient:
        """Get all records for a patient"""
        statement = select(Appointment).where(
            Appointment.id == appointment_id
        )
        appointment = self.session.exec(statement).one_or_none()
        statement = (
            select(Patient)
            .where(Patient.id == appointment.patient_id)
            .options(
                selectinload(Patient.user),
                selectinload(Patient.appointments),
                selectinload(Patient.ehr),
            )
        )
        return self.session.exec(statement).one_or_none()

    def get_doctor_records(self, doctor_id: UUID) -> List[EHR]:
        """Get all EHR records assigned to a doctor"""
        statement = select(EHR).where(EHR.doctor_id == doctor_id)
        return self.session.exec(statement).all()

    def get_pending_for_doctor(self, doctor_id: UUID) -> List[Appointment]:
        """Get pending records for a doctor"""
        statement = (
            select(Appointment)
            .where(
                (Appointment.doctor_id == doctor_id)
                & (Appointment.status != "CANCELED")
                & (Appointment.status != "PENDING")
            )
            .order_by(Appointment.scheduled_time)
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.ehr),
            )
        )
        return self.session.exec(statement).all()
