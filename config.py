"""Configuration module for OPD Token System"""
import os
from pydantic_settings import BaseSettings
from typing import Dict


class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017/opd_token_system"
    
    # Slot Configuration
    DEFAULT_SLOT_DURATION: int = 10
    DEFAULT_MAX_CAPACITY: int = 6
    
    # Priority Weights
    EMERGENCY_PRIORITY: int = 1000
    PAID_PRIORITY: int = 500
    FOLLOWUP_PRIORITY: int = 300
    ONLINE_PRIORITY: int = 200
    WALKIN_PRIORITY: int = 100
    
    # Timeout Configuration (in minutes)
    NO_SHOW_TIMEOUT: int = 15
    LATE_ARRIVAL_GRACE: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Token Types
TOKEN_TYPES = {
    "ONLINE": "ONLINE",
    "WALKIN": "WALKIN",
    "PRIORITY": "PRIORITY",
    "FOLLOWUP": "FOLLOWUP",
    "EMERGENCY": "EMERGENCY",
}

# Token Status
TOKEN_STATUS = {
    "PENDING": "PENDING",
    "CHECKED_IN": "CHECKED_IN",
    "CONSULTING": "CONSULTING",
    "COMPLETED": "COMPLETED",
    "CANCELLED": "CANCELLED",
    "NO_SHOW": "NO_SHOW",
}

# Slot Status
SLOT_STATUS = {
    "ACTIVE": "ACTIVE",
    "DELAYED": "DELAYED",
    "CANCELLED": "CANCELLED",
    "COMPLETED": "COMPLETED",
}

# Priority Weights
PRIORITY_WEIGHTS: Dict[str, int] = {
    "EMERGENCY": settings.EMERGENCY_PRIORITY,
    "PRIORITY": settings.PAID_PRIORITY,
    "FOLLOWUP": settings.FOLLOWUP_PRIORITY,
    "ONLINE": settings.ONLINE_PRIORITY,
    "WALKIN": settings.WALKIN_PRIORITY,
}
