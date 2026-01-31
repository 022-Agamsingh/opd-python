"""Routes package"""
from routes.doctor_routes import router as doctor_router
from routes.slot_routes import router as slot_router
from routes.token_routes import router as token_router

__all__ = [
    "doctor_router",
    "slot_router",
    "token_router",
]
