"""Token routes"""
from fastapi import APIRouter, HTTPException, Body
from typing import Optional
from models.token import (
    OnlineTokenCreate,
    WalkinTokenCreate,
    PriorityTokenCreate,
    FollowupTokenCreate,
    EmergencyTokenCreate,
    TokenStatusUpdate,
)
from services.token_service import token_service

# TODO: Add rate limiting to prevent abuse
# TODO: Add authentication for certain endpoints
router = APIRouter(prefix="/api/tokens", tags=["tokens"])


@router.post("/book", response_model=dict, status_code=201)
async def book_online_token(token_data: OnlineTokenCreate):
    """Book an online token"""
    try:
        token = await token_service.book_online_token(token_data)
        return {
            "success": True,
            "message": "Token booked successfully",
            "data": token.to_dict(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/walkin", response_model=dict, status_code=201)
async def generate_walkin_token(token_data: WalkinTokenCreate):
    """Generate walk-in token"""
    try:
        token = await token_service.generate_walkin_token(token_data)
        return {
            "success": True,
            "message": "Walk-in token generated successfully",
            "data": token.to_dict(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/priority", response_model=dict, status_code=201)
async def generate_priority_token(token_data: PriorityTokenCreate):
    """Generate priority (paid) token"""
    try:
        token = await token_service.generate_priority_token(token_data)
        return {
            "success": True,
            "message": "Priority token generated successfully",
            "data": token.to_dict(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/followup", response_model=dict, status_code=201)
async def generate_followup_token(token_data: FollowupTokenCreate):
    """Generate follow-up token"""
    try:
        token = await token_service.generate_followup_token(token_data)
        return {
            "success": True,
            "message": "Follow-up token generated successfully",
            "data": token.to_dict(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emergency", response_model=dict, status_code=201)
async def insert_emergency_token(token_data: EmergencyTokenCreate):
    """Insert emergency token"""
    try:
        token = await token_service.insert_emergency_token(token_data)
        return {
            "success": True,
            "message": "Emergency token inserted successfully",
            "data": token.to_dict(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{token_id}", response_model=dict)
async def get_token(token_id: str):
    """Get token by ID"""
    token = await token_service.get_token(token_id)
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    return {
        "success": True,
        "data": token.to_dict(),
    }


@router.get("/patient/{patient_id}", response_model=dict)
async def get_tokens_by_patient(patient_id: str):
    """Get all tokens for a patient"""
    try:
        tokens = await token_service.get_tokens_by_patient(patient_id)
        return {
            "success": True,
            "count": len(tokens),
            "data": [token.to_dict() for token in tokens],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/queue/{slot_id}", response_model=dict)
async def get_token_queue(slot_id: str):
    """Get token queue for a slot"""
    try:
        tokens = await token_service.get_token_queue(slot_id)
        return {
            "success": True,
            "count": len(tokens),
            "data": [token.to_dict() for token in tokens],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{token_id}/status", response_model=dict)
async def update_token_status(token_id: str, status_update: TokenStatusUpdate):
    """Update token status"""
    token = await token_service.update_token_status(token_id, status_update.status)
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    return {
        "success": True,
        "message": "Token status updated successfully",
        "data": token.to_dict(),
    }


@router.delete("/{token_id}/cancel", response_model=dict)
async def cancel_token(token_id: str, reason: Optional[str] = Body(None, embed=True)):
    """Cancel a token"""
    try:
        result = await token_service.cancel_token(token_id, reason)
        return {
            "success": True,
            "message": result["message"],
            "data": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reallocate/{slot_id}", response_model=dict)
async def reallocate_tokens(slot_id: str, target_slot_id: str = Body(..., embed=True)):
    """Reallocate tokens from a slot to another slot"""
    try:
        result = await token_service.reallocate_tokens(slot_id, target_slot_id)
        return {
            "success": True,
            "message": result["message"],
            "data": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
