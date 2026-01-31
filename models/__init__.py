"""Models package"""
from models.doctor import Doctor, DoctorCreate, DoctorResponse
from models.slot import Slot, SlotCreate, SlotResponse
from models.token import (
    Token, 
    TokenCreate,
    OnlineTokenCreate,
    WalkinTokenCreate,
    PriorityTokenCreate,
    FollowupTokenCreate,
    EmergencyTokenCreate,
    TokenResponse,
    TokenStatusUpdate
)

__all__ = [
    "Doctor",
    "DoctorCreate",
    "DoctorResponse",
    "Slot",
    "SlotCreate",
    "SlotResponse",
    "Token",
    "TokenCreate",
    "OnlineTokenCreate",
    "WalkinTokenCreate",
    "PriorityTokenCreate",
    "FollowupTokenCreate",
    "EmergencyTokenCreate",
    "TokenResponse",
    "TokenStatusUpdate",
]
