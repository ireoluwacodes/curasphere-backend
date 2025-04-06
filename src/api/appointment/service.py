from fastapi import Depends

from src.api.appointment.repository import AppointmentRepository

from src.api.sse.service import SSEService


class AppointmentService:
    def __init__(self, repository: AppointmentRepository = Depends()) -> None:
        self.repository = repository
        self.sse_service = SSEService()

    def book_appointment(self, user_id, data):
        appointment = self.repository.create(user_id, data)
        # Send SSE notification
        self.sse_service.send_notification(
            {
                "type": "appointment_booked",
                "patient_id": user_id,
                "appointment_id": appointment.id,
                "time": appointment.scheduled_time.isoformat(),
            }
        )
        return appointment

    def emergency_request(self, user_id, data):
        appointment = self.repository.create_emergency(user_id, data)
        # Send SSE notification with high priority
        self.sse_service.send_notification(
            {
                "type": "emergency_request",
                "urgency": appointment.urgency_level.value,
                "patient_id": user_id,
                "location": appointment.location,
                "appointment_id": appointment.id,
                "time": appointment.scheduled_time.isoformat(),
            },
            priority="high",
        )
        return appointment

    def list(self, user_id):
        return self.repository.list(user_id)

    def nurse_list_all(self):
        return self.repository.nurse_list_all()

    def update(self, user_id, appointment_id, data):
        return self.repository.update(user_id, appointment_id, data)

    def delete(self, user_id, appointment_id):
        return self.repository.delete(user_id, appointment_id)
