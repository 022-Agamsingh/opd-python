"""Slot service"""
from typing import List, Optional
from models.slot import Slot, SlotCreate
from database import get_database
from services.doctor_service import doctor_service
import uuid


class SlotService:
    """Slot service for business logic"""
    
    @staticmethod
    async def create_slot(slot_data: SlotCreate) -> Slot:
        """Create a new slot"""
        db = get_database()
        
        # Verify doctor exists
        doctor = await doctor_service.get_doctor(slot_data.doctor_id)
        if not doctor:
            raise ValueError(f"Doctor with ID {slot_data.doctor_id} not found")
        
        # Check for duplicate slot
        existing = await db.slots.find_one({
            "doctorId": slot_data.doctor_id,
            "date": slot_data.date,
            "startTime": slot_data.start_time,
        })
        
        if existing:
            raise ValueError("A slot with this doctor, date, and time already exists")
        
        slot = Slot(
            _id=str(uuid.uuid4()),
            doctorId=slot_data.doctor_id,
            date=slot_data.date,
            startTime=slot_data.start_time,
            endTime=slot_data.end_time,
            maxCapacity=slot_data.max_capacity,
        )
        
        await db.slots.insert_one(slot.model_dump(by_alias=True))
        return slot
    
    @staticmethod
    async def get_slot(slot_id: str) -> Optional[Slot]:
        """Get slot by ID"""
        db = get_database()
        
        slot_dict = await db.slots.find_one({"_id": slot_id})
        if not slot_dict:
            return None
        
        return Slot(**slot_dict)
    
    @staticmethod
    async def get_slots_by_doctor(doctor_id: str, date: Optional[str] = None) -> List[Slot]:
        """Get slots by doctor ID"""
        db = get_database()
        
        query = {"doctorId": doctor_id}
        if date:
            query["date"] = date
        
        slots = []
        async for slot_dict in db.slots.find(query):
            slots.append(Slot(**slot_dict))
        
        return slots
    
    @staticmethod
    async def get_available_slots(doctor_id: str, date: Optional[str] = None) -> List[Slot]:
        """Get available slots (not full)"""
        db = get_database()
        
        query = {"doctorId": doctor_id}
        if date:
            query["date"] = date
        
        slots = []
        async for slot_dict in db.slots.find(query):
            slot = Slot(**slot_dict)
            if not slot.is_full:
                slots.append(slot)
        
        return slots
    
    @staticmethod
    async def get_filled_slots(doctor_id: str, date: Optional[str] = None) -> List[Slot]:
        """Get filled/full slots"""
        db = get_database()
        
        query = {"doctorId": doctor_id}
        if date:
            query["date"] = date
        
        slots = []
        async for slot_dict in db.slots.find(query):
            slot = Slot(**slot_dict)
            if slot.is_full:
                slots.append(slot)
        
        return slots
    
    @staticmethod
    async def increment_slot_count(slot_id: str) -> Optional[Slot]:
        """Increment slot current count"""
        db = get_database()
        
        result = await db.slots.update_one(
            {"_id": slot_id},
            {"$inc": {"currentCount": 1}}
        )
        
        if result.modified_count == 0:
            return None
        
        return await SlotService.get_slot(slot_id)
    
    @staticmethod
    async def decrement_slot_count(slot_id: str) -> Optional[Slot]:
        """Decrement slot current count"""
        db = get_database()
        
        slot = await SlotService.get_slot(slot_id)
        if not slot or slot.current_count <= 0:
            return slot
        
        result = await db.slots.update_one(
            {"_id": slot_id},
            {"$inc": {"currentCount": -1}}
        )
        
        if result.modified_count == 0:
            return None
        
        return await SlotService.get_slot(slot_id)
    
    @staticmethod
    async def mark_delayed(slot_id: str, delay_minutes: int) -> Optional[Slot]:
        """Mark slot as delayed"""
        db = get_database()
        
        result = await db.slots.update_one(
            {"_id": slot_id},
            {
                "$set": {
                    "isDelayed": True,
                    "delayMinutes": delay_minutes,
                    "status": "DELAYED"
                }
            }
        )
        
        if result.modified_count == 0:
            return None
        
        return await SlotService.get_slot(slot_id)
    
    @staticmethod
    async def update_slot_status(slot_id: str, status: str) -> Optional[Slot]:
        """Update slot status"""
        db = get_database()
        
        result = await db.slots.update_one(
            {"_id": slot_id},
            {"$set": {"status": status}}
        )
        
        if result.modified_count == 0:
            return None
        
        return await SlotService.get_slot(slot_id)
    
    @staticmethod
    async def get_slot_stats(slot_id: str) -> dict:
        """Get slot statistics"""
        db = get_database()
        
        slot = await SlotService.get_slot(slot_id)
        if not slot:
            raise ValueError(f"Slot with ID {slot_id} not found")
        
        # Count tokens by status
        token_stats = {}
        async for status_doc in db.tokens.aggregate([
            {"$match": {"slotId": slot_id}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]):
            token_stats[status_doc["_id"]] = status_doc["count"]
        
        return {
            "slotId": slot_id,
            "maxCapacity": slot.max_capacity,
            "currentCount": slot.current_count,
            "availableCapacity": slot.available_capacity,
            "isFull": slot.is_full,
            "isDelayed": slot.is_delayed,
            "delayMinutes": slot.delay_minutes,
            "status": slot.status,
            "tokenStats": token_stats,
        }


# Create singleton instance
slot_service = SlotService()
