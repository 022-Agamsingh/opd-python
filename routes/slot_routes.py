"""Slot routes"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from models.slot import SlotCreate, SlotResponse
from services.slot_service import slot_service

router = APIRouter(prefix="/api/slots", tags=["slots"])


@router.post("", response_model=dict, status_code=201)
async def create_slot(slot_data: SlotCreate):
    """Create a new slot"""
    try:
        slot = await slot_service.create_slot(slot_data)
        return {
            "success": True,
            "message": "Slot created successfully",
            "data": slot.to_dict(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{slot_id}", response_model=dict)
async def get_slot(slot_id: str):
    """Get slot by ID"""
    slot = await slot_service.get_slot(slot_id)
    
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    return {
        "success": True,
        "data": slot.to_dict(),
    }


@router.get("/doctor/{doctor_id}", response_model=dict)
async def get_slots_by_doctor(doctor_id: str, date: Optional[str] = Query(None)):
    """Get all slots for a doctor"""
    try:
        slots = await slot_service.get_slots_by_doctor(doctor_id, date)
        return {
            "success": True,
            "count": len(slots),
            "data": [slot.to_dict() for slot in slots],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/doctor/{doctor_id}/available", response_model=dict)
async def get_available_slots(doctor_id: str, date: Optional[str] = Query(None)):
    """Get available slots for a doctor"""
    try:
        slots = await slot_service.get_available_slots(doctor_id, date)
        return {
            "success": True,
            "count": len(slots),
            "data": [slot.to_dict() for slot in slots],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/doctor/{doctor_id}/filled", response_model=dict)
async def get_filled_slots(doctor_id: str, date: Optional[str] = Query(None)):
    """Get filled/full slots for a doctor"""
    try:
        slots = await slot_service.get_filled_slots(doctor_id, date)
        return {
            "success": True,
            "count": len(slots),
            "data": [slot.to_dict() for slot in slots],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{slot_id}/delay", response_model=dict)
async def mark_slot_delayed(slot_id: str, delay_minutes: int = Query(..., gt=0)):
    """Mark slot as delayed"""
    slot = await slot_service.mark_delayed(slot_id, delay_minutes)
    
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    return {
        "success": True,
        "message": f"Slot marked as delayed by {delay_minutes} minutes",
        "data": slot.to_dict(),
    }


@router.get("/{slot_id}/stats", response_model=dict)
async def get_slot_stats(slot_id: str):
    """Get slot statistics"""
    try:
        stats = await slot_service.get_slot_stats(slot_id)
        return {
            "success": True,
            "data": stats,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
