"""Token model"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
from config import TOKEN_STATUS, TOKEN_TYPES

# Note: Using Pydantic v2 with alias support for MongoDB compatibility


class Token(BaseModel):
    """Token model"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    token_number: str = Field(..., alias="tokenNumber")
    patient_id: str = Field(..., alias="patientId")
    patient_name: str = Field(..., alias="patientName")
    slot_id: str = Field(..., alias="slotId")
    type: str
    priority: int
    queue_position: int = Field(..., alias="queuePosition")
    estimated_time: str = Field(..., alias="estimatedTime")
    status: str = Field(default=TOKEN_STATUS["PENDING"])
    phone_number: Optional[str] = Field(default=None, alias="phoneNumber")
    check_in_time: Optional[datetime] = Field(default=None, alias="checkInTime")
    completed_time: Optional[datetime] = Field(default=None, alias="completedTime")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "token-123",
                "tokenNumber": "T001",
                "patientId": "patient-456",
                "patientName": "John Doe",
                "slotId": "slot-789",
                "type": "ONLINE",
                "priority": 200,
                "queuePosition": 1,
                "estimatedTime": "2024-01-15T09:00:00",
                "status": "PENDING",
                "phoneNumber": "1234567890",
            }
        }
    
    def to_dict(self):
        """Convert to dictionary"""
        data = self.model_dump(by_alias=True)
        data["id"] = data["_id"]
        return data


class TokenCreate(BaseModel):
    """Token creation base model"""
    
    slot_id: str = Field(..., alias="slotId")
    patient_name: str = Field(..., alias="patientName")
    phone_number: Optional[str] = Field(default=None, alias="phoneNumber")
    
    class Config:
        populate_by_name = True


class OnlineTokenCreate(TokenCreate):
    """Online token creation model"""
    
    patient_id: str = Field(..., alias="patientId")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "slotId": "slot-789",
                "patientId": "patient-456",
                "patientName": "John Doe",
                "phoneNumber": "1234567890",
            }
        }


class WalkinTokenCreate(TokenCreate):
    """Walk-in token creation model"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "slotId": "slot-789",
                "patientName": "Jane Doe",
                "phoneNumber": "0987654321",
            }
        }


class PriorityTokenCreate(OnlineTokenCreate):
    """Priority token creation model"""
    pass


class FollowupTokenCreate(OnlineTokenCreate):
    """Follow-up token creation model"""
    pass


class EmergencyTokenCreate(TokenCreate):
    """Emergency token creation model"""
    pass


class TokenResponse(BaseModel):
    """Token response model"""
    
    id: str
    token_number: str = Field(..., alias="tokenNumber")
    patient_id: str = Field(..., alias="patientId")
    patient_name: str = Field(..., alias="patientName")
    slot_id: str = Field(..., alias="slotId")
    type: str
    priority: int
    queue_position: int = Field(..., alias="queuePosition")
    estimated_time: str = Field(..., alias="estimatedTime")
    status: str
    phone_number: Optional[str] = Field(default=None, alias="phoneNumber")
    
    class Config:
        populate_by_name = True


class TokenStatusUpdate(BaseModel):
    """Token status update model"""
    
    status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "CHECKED_IN",
            }
        }
