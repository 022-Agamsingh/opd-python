"""Doctor model"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class Doctor(BaseModel):
    """Doctor model"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    name: str
    specialization: str
    opd_days: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Dr. Smith",
                "specialization": "Cardiology",
                "opd_days": ["Monday", "Wednesday", "Friday"],
            }
        }
    
    def to_dict(self):
        """Convert to dictionary"""
        data = self.model_dump(by_alias=True)
        data["id"] = data["_id"]
        return data


class DoctorCreate(BaseModel):
    """Doctor creation model"""
    
    name: str
    specialization: str
    opd_days: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Dr. Smith",
                "specialization": "Cardiology",
                "opd_days": ["Monday", "Wednesday", "Friday"],
            }
        }


class DoctorResponse(BaseModel):
    """Doctor response model"""
    
    id: str
    name: str
    specialization: str
    opd_days: List[str]
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Dr. Smith",
                "specialization": "Cardiology",
                "opd_days": ["Monday", "Wednesday", "Friday"],
                "created_at": "2024-01-01T10:00:00",
            }
        }
