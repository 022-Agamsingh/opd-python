"""Doctor service"""
from typing import List, Optional
from models.doctor import Doctor, DoctorCreate
from database import get_database
import uuid


class DoctorService:
    """Doctor service for business logic"""
    
    @staticmethod
    async def create_doctor(doctor_data: DoctorCreate) -> Doctor:
        """Create a new doctor"""
        db = get_database()
        
        doctor = Doctor(
            _id=str(uuid.uuid4()),
            name=doctor_data.name,
            specialization=doctor_data.specialization,
            opd_days=doctor_data.opd_days,
        )
        
        await db.doctors.insert_one(doctor.model_dump(by_alias=True))
        return doctor
    
    @staticmethod
    async def get_doctor(doctor_id: str) -> Optional[Doctor]:
        """Get doctor by ID"""
        db = get_database()
        
        doctor_dict = await db.doctors.find_one({"_id": doctor_id})
        if not doctor_dict:
            return None
        
        return Doctor(**doctor_dict)
    
    @staticmethod
    async def get_all_doctors() -> List[Doctor]:
        """Get all doctors"""
        db = get_database()
        
        doctors = []
        async for doctor_dict in db.doctors.find():
            doctors.append(Doctor(**doctor_dict))
        
        return doctors
    
    @staticmethod
    async def get_doctors_by_specialization(specialization: str) -> List[Doctor]:
        """Get doctors by specialization"""
        db = get_database()
        
        doctors = []
        async for doctor_dict in db.doctors.find({"specialization": specialization}):
            doctors.append(Doctor(**doctor_dict))
        
        return doctors
    
    @staticmethod
    async def update_doctor(doctor_id: str, update_data: dict) -> Optional[Doctor]:
        """Update doctor"""
        db = get_database()
        
        result = await db.doctors.update_one(
            {"_id": doctor_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            return None
        
        return await DoctorService.get_doctor(doctor_id)
    
    @staticmethod
    async def delete_doctor(doctor_id: str) -> bool:
        """Delete doctor"""
        db = get_database()
        
        result = await db.doctors.delete_one({"_id": doctor_id})
        return result.deleted_count > 0


# Create singleton instance
doctor_service = DoctorService()
