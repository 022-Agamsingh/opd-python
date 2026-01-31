"""Slot model"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
from config import SLOT_STATUS


class Slot(BaseModel):
    """Slot model"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    doctor_id: str = Field(..., alias="doctorId")
    date: str
    start_time: str = Field(..., alias="startTime")
    end_time: str = Field(..., alias="endTime")
    max_capacity: int = Field(..., alias="maxCapacity", ge=1)
    current_count: int = Field(default=0, alias="currentCount")
    is_delayed: bool = Field(default=False, alias="isDelayed")
    delay_minutes: int = Field(default=0, alias="delayMinutes")
    status: str = Field(default=SLOT_STATUS["ACTIVE"])
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "slot-123",
                "doctorId": "doctor-456",
                "date": "2024-01-15",
                "startTime": "09:00",
                "endTime": "10:00",
                "maxCapacity": 20,
                "currentCount": 5,
                "isDelayed": False,
                "delayMinutes": 0,
                "status": "ACTIVE",
            }
        }
    
    @property
    def available_capacity(self) -> int:
        """Get available capacity"""
        return self.max_capacity - self.current_count
    
    @property
    def is_full(self) -> bool:
        """Check if slot is full"""
        return self.current_count >= self.max_capacity
    
    def to_dict(self):
        """Convert to dictionary"""
        data = self.model_dump(by_alias=True)
        data["id"] = data["_id"]
        data["availableCapacity"] = self.available_capacity
        data["isFull"] = self.is_full
        return data


class SlotCreate(BaseModel):
    """Slot creation model"""
    
    doctor_id: str = Field(..., alias="doctorId")
    date: str
    start_time: str = Field(..., alias="startTime")
    end_time: str = Field(..., alias="endTime")
    max_capacity: int = Field(..., alias="maxCapacity", ge=1)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "doctorId": "doctor-456",
                "date": "2024-01-15",
                "startTime": "09:00",
                "endTime": "10:00",
                "maxCapacity": 20,
            }
        }


class SlotResponse(BaseModel):
    """Slot response model"""
    
    id: str
    doctor_id: str = Field(..., alias="doctorId")
    date: str
    start_time: str = Field(..., alias="startTime")
    end_time: str = Field(..., alias="endTime")
    max_capacity: int = Field(..., alias="maxCapacity")
    current_count: int = Field(..., alias="currentCount")
    available_capacity: int = Field(..., alias="availableCapacity")
    is_full: bool = Field(..., alias="isFull")
    is_delayed: bool = Field(..., alias="isDelayed")
    delay_minutes: int = Field(..., alias="delayMinutes")
    status: str
    
    class Config:
        populate_by_name = True
