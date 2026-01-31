"""Token service - Core allocation algorithm"""
from typing import List, Optional
from datetime import datetime, timedelta
from models.token import Token, OnlineTokenCreate, WalkinTokenCreate, PriorityTokenCreate, FollowupTokenCreate, EmergencyTokenCreate
from database import get_database
from services.slot_service import slot_service
from config import TOKEN_TYPES, TOKEN_STATUS, PRIORITY_WEIGHTS
import uuid
import time

# Debug flag - set True for detailed logging during development
DEBUG = False


class TokenService:
    """Token service for core allocation algorithm and business logic"""
    
    @staticmethod
    async def allocate_token(
        slot_id: str,
        patient_id: str,
        patient_name: str,
        token_type: str,
        phone_number: Optional[str] = None
    ) -> Token:
        """
        Core Token Allocation Algorithm
        Enforces slot limits, handles priorities, and manages edge cases
        """
        # Validate slot
        slot = await slot_service.get_slot(slot_id)
        if not slot:
            raise ValueError(f"Slot with ID {slot_id} not found")
        
        # Check if slot is full
        if slot.is_full:
            raise ValueError("Slot is full. Token cannot be allocated.")
        
        # Calculate priority score
        priority_score = TokenService._calculate_priority_score(token_type)
        
        # Create token
        token = Token(
            _id=str(uuid.uuid4()),
            tokenNumber="T000",  # Temporary, will be assigned
            patientId=patient_id,
            patientName=patient_name,
            slotId=slot_id,
            type=token_type,
            priority=priority_score,
            queuePosition=0,  # Temporary, will be assigned
            estimatedTime="",  # Temporary, will be calculated
            phoneNumber=phone_number,
        )
        
        # Assign token number based on priority
        await TokenService._assign_token_number(token, slot_id)
        
        # Update slot capacity
        await slot_service.increment_slot_count(slot_id)
        
        # Calculate estimated time
        await TokenService._calculate_estimated_time(token)
        
        # Save token
        db = get_database()
        await db.tokens.insert_one(token.model_dump(by_alias=True))
        
        return token
    
    @staticmethod
    def _calculate_priority_score(token_type: str) -> int:
        """
        Calculate priority score for token
        Base priority from type + time factor for FIFO within same priority
        """
        # Base score from priority weights config
        base_score = PRIORITY_WEIGHTS.get(token_type, 100)
        
        # Add small time factor to ensure FIFO within same priority level
        # Dividing by 1B keeps it small enough to not affect priority order
        # but large enough to maintain chronological order
        time_factor = time.time() / 1000000000
        
        score = int(base_score + time_factor)
        
        # Uncomment for debugging priority issues
        # if DEBUG:
        #     print(f"Priority calc: {token_type} -> {score} (base: {base_score})")
        
        return score
    
    @staticmethod
    async def _assign_token_number(new_token: Token, slot_id: str):
        """
        Assign token number based on priority queue
        Sorts all active tokens and assigns sequential positions
        """
        db = get_database()
        
        # Get all active tokens in slot (exclude CANCELLED and NO_SHOW)
        existing_tokens = []
        async for token_dict in db.tokens.find({
            "slotId": slot_id,
            "status": {"$nin": [TOKEN_STATUS["CANCELLED"], TOKEN_STATUS["NO_SHOW"]]}
        }):
            existing_tokens.append(Token(**token_dict))
        
        # Add new token to list
        existing_tokens.append(new_token)
        
        # Sort by priority score (higher first = descending order)
        existing_tokens.sort(key=lambda t: t.priority, reverse=True)
        
        # Assign positions and token numbers
        for index, token in enumerate(existing_tokens):
            token.queue_position = index + 1
            token.token_number = f"T{str(index + 1).zfill(3)}"
            
            # Update in database if not the new token
            if token.id != new_token.id:
                await db.tokens.update_one(
                    {"_id": token.id},
                    {
                        "$set": {
                            "queuePosition": token.queue_position,
                            "tokenNumber": token.token_number,
                        }
                    }
                )
        
        # Update new token's position and number
        new_token.queue_position = existing_tokens[existing_tokens.index(new_token)].queue_position
        new_token.token_number = existing_tokens[existing_tokens.index(new_token)].token_number
    
    @staticmethod
    async def _calculate_estimated_time(token: Token):
        """Calculate estimated time for patient"""
        slot = await slot_service.get_slot(token.slot_id)
        if not slot:
            return
        
        # Parse slot start time
        try:
            hours, minutes = map(int, slot.start_time.split(':'))
            
            # Average consultation time: 10 minutes
            avg_consultation_time = 10
            estimated_minutes = (token.queue_position - 1) * avg_consultation_time
            
            # Create estimated date
            estimated_date = datetime.strptime(slot.date, "%Y-%m-%d")
            estimated_date = estimated_date.replace(hour=hours, minute=minutes)
            estimated_date += timedelta(minutes=estimated_minutes)
            
            # Add delay if slot is delayed
            if slot.is_delayed:
                estimated_date += timedelta(minutes=slot.delay_minutes)
            
            token.estimated_time = estimated_date.isoformat()
        except Exception as e:
            # Default to current time if parsing fails
            token.estimated_time = datetime.utcnow().isoformat()
    
    @staticmethod
    async def book_online_token(token_data: OnlineTokenCreate) -> Token:
        """Book online token"""
        return await TokenService.allocate_token(
            slot_id=token_data.slot_id,
            patient_id=token_data.patient_id,
            patient_name=token_data.patient_name,
            token_type=TOKEN_TYPES["ONLINE"],
            phone_number=token_data.phone_number,
        )
    
    @staticmethod
    async def generate_walkin_token(token_data: WalkinTokenCreate) -> Token:
        """Generate walk-in token"""
        patient_id = f"WALKIN-{int(time.time() * 1000)}"
        return await TokenService.allocate_token(
            slot_id=token_data.slot_id,
            patient_id=patient_id,
            patient_name=token_data.patient_name,
            token_type=TOKEN_TYPES["WALKIN"],
            phone_number=token_data.phone_number,
        )
    
    @staticmethod
    async def generate_priority_token(token_data: PriorityTokenCreate) -> Token:
        """Generate priority (paid) token"""
        return await TokenService.allocate_token(
            slot_id=token_data.slot_id,
            patient_id=token_data.patient_id,
            patient_name=token_data.patient_name,
            token_type=TOKEN_TYPES["PRIORITY"],
            phone_number=token_data.phone_number,
        )
    
    @staticmethod
    async def generate_followup_token(token_data: FollowupTokenCreate) -> Token:
        """Generate follow-up token"""
        return await TokenService.allocate_token(
            slot_id=token_data.slot_id,
            patient_id=token_data.patient_id,
            patient_name=token_data.patient_name,
            token_type=TOKEN_TYPES["FOLLOWUP"],
            phone_number=token_data.phone_number,
        )
    
    @staticmethod
    async def insert_emergency_token(token_data: EmergencyTokenCreate) -> Token:
        """
        Insert emergency token
        Emergency tokens get highest priority and may cause reallocation
        """
        patient_id = f"EMERGENCY-{int(time.time() * 1000)}"
        slot = await slot_service.get_slot(token_data.slot_id)
        
        if not slot:
            raise ValueError(f"Slot with ID {token_data.slot_id} not found")
        
        # If slot is full, temporarily extend capacity by 1 for emergency
        if slot.is_full:
            print(f"EMERGENCY: Extending slot {token_data.slot_id} capacity for emergency case")
            db = get_database()
            await db.slots.update_one(
                {"_id": token_data.slot_id},
                {"$inc": {"maxCapacity": 1}}
            )
        
        token = await TokenService.allocate_token(
            slot_id=token_data.slot_id,
            patient_id=patient_id,
            patient_name=token_data.patient_name,
            token_type=TOKEN_TYPES["EMERGENCY"],
            phone_number=token_data.phone_number,
        )
        
        # Re-sort all tokens in the slot (already done in allocate_token)
        return token
    
    @staticmethod
    async def get_token(token_id: str) -> Optional[Token]:
        """Get token by ID"""
        db = get_database()
        
        token_dict = await db.tokens.find_one({"_id": token_id})
        if not token_dict:
            return None
        
        return Token(**token_dict)
    
    @staticmethod
    async def get_tokens_by_patient(patient_id: str) -> List[Token]:
        """Get all tokens for a patient"""
        db = get_database()
        
        tokens = []
        async for token_dict in db.tokens.find({"patientId": patient_id}):
            tokens.append(Token(**token_dict))
        
        return tokens
    
    @staticmethod
    async def get_token_queue(slot_id: str) -> List[Token]:
        """Get token queue for a slot (sorted by position)"""
        db = get_database()
        
        tokens = []
        async for token_dict in db.tokens.find({
            "slotId": slot_id,
            "status": {"$nin": [TOKEN_STATUS["CANCELLED"], TOKEN_STATUS["NO_SHOW"]]}
        }).sort("queuePosition", 1):
            tokens.append(Token(**token_dict))
        
        return tokens
    
    @staticmethod
    async def update_token_status(token_id: str, status: str) -> Optional[Token]:
        """Update token status"""
        db = get_database()
        
        update_data = {"status": status}
        
        # Set timestamps based on status
        if status == TOKEN_STATUS["CHECKED_IN"]:
            update_data["checkInTime"] = datetime.utcnow()
        elif status == TOKEN_STATUS["COMPLETED"]:
            update_data["completedTime"] = datetime.utcnow()
        
        result = await db.tokens.update_one(
            {"_id": token_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            return None
        
        return await TokenService.get_token(token_id)
    
    @staticmethod
    async def cancel_token(token_id: str, reason: Optional[str] = None) -> dict:
        """Cancel a token"""
        token = await TokenService.get_token(token_id)
        
        if not token:
            raise ValueError(f"Token with ID {token_id} not found")
        
        if token.status == TOKEN_STATUS["CANCELLED"]:
            raise ValueError("Token is already cancelled")
        
        if token.status == TOKEN_STATUS["COMPLETED"]:
            raise ValueError("Cannot cancel a completed token")
        
        # Update token status
        await TokenService.update_token_status(token_id, TOKEN_STATUS["CANCELLED"])
        
        # Decrement slot count
        await slot_service.decrement_slot_count(token.slot_id)
        
        # Reorder remaining tokens
        await TokenService._reorder_slot_tokens(token.slot_id)
        
        return {
            "tokenId": token_id,
            "status": "cancelled",
            "reason": reason,
            "message": "Token cancelled successfully and queue reordered",
        }
    
    @staticmethod
    async def _reorder_slot_tokens(slot_id: str):
        """Reorder all tokens in a slot based on priority"""
        db = get_database()
        
        # Get all active tokens
        tokens = []
        async for token_dict in db.tokens.find({
            "slotId": slot_id,
            "status": {"$nin": [TOKEN_STATUS["CANCELLED"], TOKEN_STATUS["NO_SHOW"], TOKEN_STATUS["COMPLETED"]]}
        }):
            tokens.append(Token(**token_dict))
        
        # Sort by priority
        tokens.sort(key=lambda t: t.priority, reverse=True)
        
        # Reassign positions and recalculate times
        for index, token in enumerate(tokens):
            token.queue_position = index + 1
            token.token_number = f"T{str(index + 1).zfill(3)}"
            await TokenService._calculate_estimated_time(token)
            
            # Update in database
            await db.tokens.update_one(
                {"_id": token.id},
                {
                    "$set": {
                        "queuePosition": token.queue_position,
                        "tokenNumber": token.token_number,
                        "estimatedTime": token.estimated_time,
                    }
                }
            )
    
    @staticmethod
    async def reallocate_tokens(slot_id: str, target_slot_id: str) -> dict:
        """Reallocate tokens from one slot to another"""
        # Get source slot
        source_slot = await slot_service.get_slot(slot_id)
        if not source_slot:
            raise ValueError(f"Source slot with ID {slot_id} not found")
        
        # Get target slot
        target_slot = await slot_service.get_slot(target_slot_id)
        if not target_slot:
            raise ValueError(f"Target slot with ID {target_slot_id} not found")
        
        # Get all pending tokens from source slot
        db = get_database()
        tokens_to_reallocate = []
        async for token_dict in db.tokens.find({
            "slotId": slot_id,
            "status": TOKEN_STATUS["PENDING"]
        }):
            tokens_to_reallocate.append(Token(**token_dict))
        
        if not tokens_to_reallocate:
            return {
                "message": "No tokens to reallocate",
                "reallocated": 0,
            }
        
        # Check if target slot has capacity
        available = target_slot.available_capacity
        if available < len(tokens_to_reallocate):
            raise ValueError(f"Target slot only has capacity for {available} tokens, but {len(tokens_to_reallocate)} need reallocation")
        
        reallocated_count = 0
        for token in tokens_to_reallocate:
            # Update token's slot ID
            await db.tokens.update_one(
                {"_id": token.id},
                {"$set": {"slotId": target_slot_id}}
            )
            
            # Update slot counts
            await slot_service.decrement_slot_count(slot_id)
            await slot_service.increment_slot_count(target_slot_id)
            
            reallocated_count += 1
        
        # Reorder tokens in target slot
        await TokenService._reorder_slot_tokens(target_slot_id)
        
        return {
            "message": "Tokens reallocated successfully",
            "reallocated": reallocated_count,
            "sourceSlot": slot_id,
            "targetSlot": target_slot_id,
        }


# Create singleton instance
token_service = TokenService()
