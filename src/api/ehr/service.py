from fastapi import Depends
from uuid import UUID

from src.api.ehr.repository import EHRRepository
from src.api.sse.service import SSEService


class EHRService:
    def __init__(
        self,
        repository: EHRRepository = Depends(),
    ) -> None:
        self.repository = repository
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

    def update_diagnosis(self, appointment_id: UUID, doctor_id: UUID, data):
        """Update diagnosis and prescription"""
        return self.repository.update_diagnosis(
            appointment_id, doctor_id, data
        )

    def complete_ehr(self, appointment_id: UUID, doctor_id: UUID):
        """Mark EHR as completed"""
        return self.repository.complete_ehr(appointment_id, doctor_id)

    def get_patient_records(self, appointment_id: UUID):
        """Get all EHR records for a patient"""
        return self.repository.get_patient_records(appointment_id)

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
