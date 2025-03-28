from fastapi import APIRouter, Depends, HTTPException, status
from src.api.appointment.service import AppointmentService
from src.api.appointment.schema import AppointmentInput, EmergencyInput
from src.api.deps import get_current_user
from src.api.user.models import User

router = APIRouter()


@router.post("/book")
async def book_appointment(
    data: AppointmentInput,
    appointment_service: AppointmentService = Depends(),
    current_user: User = Depends(get_current_user),
):
    appointment = appointment_service.book_appointment(current_user.id, data)
    return {"success": True, "appointment": appointment}


@router.post("/emergency")
async def emergency_request(
    data: EmergencyInput,
    appointment_service: AppointmentService = Depends(),
    current_user: User = Depends(get_current_user),
):
    """Submit an emergency appointment request"""
    appointment = appointment_service.emergency_request(current_user.id, data)
    return {"success": True, "appointment": appointment}


@router.get("/mine")
async def list_appointments(
    appointment_service: AppointmentService = Depends(),
    current_user: User = Depends(get_current_user),
):
    """List all appointments for the current user"""
    appointments = appointment_service.list(current_user)
    return {"appointments": appointments}


@router.put("/update/{appointment_id}")
async def update_appointment(
    appointment_id: int,
    data: AppointmentInput,
    appointment_service: AppointmentService = Depends(),
    current_user: User = Depends(get_current_user),
):
    """Update an appointment"""
    appointment = appointment_service.update(
        current_user, appointment_id, data
    )
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    return {"success": True, "appointment": appointment}


@router.delete("/delete/{appointment_id}")
async def delete_appointment(
    appointment_id: int,
    appointment_service: AppointmentService = Depends(),
    current_user: User = Depends(get_current_user),
):
    """Delete an appointment"""
    result = appointment_service.delete(current_user.id, appointment_id)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    return {"success": True}
