from fastapi import Depends
from uuid import UUID

from src.api.ehr.repository import EHRRepository
from src.api.appointment.repository import AppointmentRepository
from src.api.sse.service import SSEService


class EHRService:
    def __init__(
        self,
        repository: EHRRepository = Depends(),
        appointment_repository: AppointmentRepository = Depends(),
    ) -> None:
        self.repository = repository
        self.appointment_repository = appointment_repository
        self.sse_service = SSEService()

    def record_vitals(self, appointment_id: UUID, data, nurse_id: UUID):
        """Record vital signs"""
        ehr = self.repository.update_vitals(appointment_id, data, nurse_id)
        return ehr

    def assign_doctor(self, doctor_id: UUID, appointment_id: UUID):
        """Assign a doctor to an appointment"""
        ehr = self.repository.assign_doctor(doctor_id, appointment_id)
        if ehr:
            # Notify the assigned doctor
            self.sse_service.send_notification(
                {
                    "type": "patient_vitals_recorded",
                    "recipient_id": str(ehr.doctor_id),
                    "patient_id": str(ehr.patient_id),
                },
            )
        return ehr

    def update_diagnosis(self, ehr_id: int, doctor_id: UUID, data):
        """Update diagnosis and prescription"""
        ehr = self.repository.update_diagnosis(ehr_id, doctor_id, data)

        if ehr:
            # Update appointment status
            appointment = self.appointment_repository.get(
                None, ehr.appointment_id
            )
            if appointment:
                appointment.status = "completed"
                self.appointment_repository.session.add(appointment)
                self.appointment_repository.session.commit()

            # Notify the patient
            self.sse_service.send_notification(
                {
                    "type": "diagnosis_updated",
                    "ehr_id": ehr.id,
                    "appointment_id": str(ehr.appointment_id),
                },
                recipient_id=str(ehr.patient_id),
            )

        return ehr

    def complete_ehr(self, ehr_id: int, doctor_id: UUID):
        """Mark EHR as completed"""
        return self.repository.complete_ehr(ehr_id, doctor_id)

    def get_patient_records(self, patient_id: UUID):
        """Get all EHR records for a patient"""
        return self.repository.get_patient_records(patient_id)

    def get_doctor_records(self, doctor_id: UUID):
        """Get all EHR records assigned to a doctor"""
        return self.repository.get_doctor_records(doctor_id)

    def get_pending_for_doctor(self, doctor_id: UUID):
        """Get pending EHR records for a doctor"""
        return self.repository.get_pending_for_doctor(doctor_id)

    def get_by_appointment(self, appointment_id: UUID):
        """Get EHR by appointment ID"""
        return self.repository.get_by_appointment(appointment_id)

    def get_by_id(self, ehr_id: int):
        """Get EHR by ID"""
        return self.repository.get_by_id(ehr_id)
