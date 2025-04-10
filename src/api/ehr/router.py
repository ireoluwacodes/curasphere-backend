from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from src.api.ehr.service import EHRService
from src.api.ehr.schema import (
    AppointmentListResponse,
    VitalSignsInput,
    DiagnosisInput,
)
from src.api.deps import get_current_user
from src.api.user.models import User, UserRole

router = APIRouter()


@router.put("/assign/{doctor_id}/{appointment_id}")
async def assign_doctor(
    doctor_id: UUID,
    appointment_id: UUID,
    ehr_service: EHRService = Depends(),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.nurse:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only nurses can assign doctors",
        )

    ehr = ehr_service.assign_doctor(doctor_id, appointment_id)
    if not ehr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="EHR record not found",
        )
    return {"message": "Doctor Assigned Successfully"}


@router.post("/vitals/{appointment_id}")
async def record_vitals(
    appointment_id: UUID,
    data: VitalSignsInput,
    ehr_service: EHRService = Depends(),
    current_user: User = Depends(get_current_user),
):
    """Record vital signs (nurses only)"""
    if current_user.role != UserRole.nurse:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only nurses can record vital signs",
        )

    ehr_service.record_vitals(appointment_id, data, current_user.nurse.id)
    return {"message": "vitals recorded successfully"}


@router.put("/diagnosis/{ehr_id}")
async def update_diagnosis(
    ehr_id: int,
    data: DiagnosisInput,
    ehr_service: EHRService = Depends(),
    current_user: User = Depends(get_current_user),
):
    """Update diagnosis and prescription (doctors only)"""
    if current_user.role != UserRole.doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update diagnosis",
        )

    ehr = ehr_service.update_diagnosis(ehr_id, current_user.id, data)
    if not ehr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="EHR record not found or you're not the assigned doctor",
        )
    return {"success": True, "ehr": ehr}


@router.put("/complete/{ehr_id}")
async def complete_ehr(
    ehr_id: int,
    ehr_service: EHRService = Depends(),
    current_user: User = Depends(get_current_user),
):
    """Mark EHR as completed (doctors only)"""
    if current_user.role != UserRole.doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can complete EHR records",
        )

    ehr = ehr_service.complete_ehr(ehr_id, current_user.doctor.id)
    if not ehr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="EHR record not found or you're not the assigned doctor",
        )
    return {"success": True, "ehr": ehr}


@router.get("/patient/{patient_id}")
async def get_patient_records(
    patient_id: UUID,
    ehr_service: EHRService = Depends(),
    current_user: User = Depends(get_current_user),
):
    """Get all EHR records for a patient"""
    records = ehr_service.get_patient_records(patient_id)
    return {"records": records}


@router.get(
    "/doctor/pending",
    response_model=AppointmentListResponse,
)
async def get_pending_for_doctor(
    ehr_service: EHRService = Depends(),
    current_user: User = Depends(get_current_user),
):
    """Get pending EHR records for the current doctor"""
    if current_user.role != UserRole.doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can access this endpoint",
        )
    records = ehr_service.get_pending_for_doctor(current_user.doctor.id)
    return {"records": records}


@router.get("/doctor/all")
async def get_doctor_records(
    ehr_service: EHRService = Depends(),
    current_user: User = Depends(get_current_user),
):
    """Get pending EHR records for the current doctor"""
    if current_user.role != UserRole.doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can access this endpoint",
        )

    records = ehr_service.get_doctor_records(current_user.doctor.id)
    return {"records": records}


@router.get("/appointment/{appointment_id}")
async def get_by_appointment(
    appointment_id: UUID,
    ehr_service: EHRService = Depends(),
    current_user: User = Depends(get_current_user),
):
    """Get EHR by appointment ID"""
    ehr = ehr_service.get_by_appointment(appointment_id)
    if not ehr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="EHR record not found for this appointment",
        )
    return {"ehr": ehr}


@router.get("/{ehr_id}")
async def get_by_id(
    ehr_id: int,
    ehr_service: EHRService = Depends(),
    current_user: User = Depends(get_current_user),
):
    """Get EHR by ID"""
    ehr = ehr_service.get_by_id(ehr_id)
    if not ehr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="EHR record not found",
        )
    return {"ehr": ehr}
