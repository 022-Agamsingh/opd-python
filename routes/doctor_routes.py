"""Doctor routes"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from models.doctor import DoctorCreate, DoctorResponse
from services.doctor_service import doctor_service

router = APIRouter(prefix="/api/doctors", tags=["doctors"])


@router.post("", response_model=dict, status_code=201)
async def create_doctor(doctor_data: DoctorCreate):
    """Create a new doctor"""
    try:
        doctor = await doctor_service.create_doctor(doctor_data)
        return {
            "success": True,
            "message": "Doctor created successfully",
            "data": doctor.to_dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=dict)
async def get_doctors(specialization: Optional[str] = Query(None)):
    """Get all doctors or filter by specialization"""
    try:
        if specialization:
            doctors = await doctor_service.get_doctors_by_specialization(specialization)
        else:
            doctors = await doctor_service.get_all_doctors()
        
        return {
            "success": True,
            "count": len(doctors),
            "data": [doctor.to_dict() for doctor in doctors],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{doctor_id}", response_model=dict)
async def get_doctor(doctor_id: str):
    """Get doctor by ID"""
    doctor = await doctor_service.get_doctor(doctor_id)
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return {
        "success": True,
        "data": doctor.to_dict(),
    }
