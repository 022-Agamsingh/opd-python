"""OPD Simulation - Complete day simulation"""
import asyncio
import sys
from datetime import datetime, date
from services.doctor_service import doctor_service
from services.slot_service import slot_service
from services.token_service import token_service
from database import connect_db, disconnect_db

# Simulation parameters - tweak these to test different scenarios
NUM_DOCTORS = 3
SLOTS_PER_DOCTOR = 3


class OPDSimulation:
    """OPD Simulation for One Day"""
    
    def __init__(self):
        self.doctors = []
        self.slots = []
        self.tokens = []
        self.events = []
    
    def log(self, message: str, log_type: str = "INFO"):
        """Log simulation events with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] [{log_type}] {message}"
        print(log_message)  # Print to console for real-time monitoring
        self.events.append({"timestamp": timestamp, "type": log_type, "message": message})
    
    async def initialize_opd(self):
        """Initialize doctors and slots"""
        self.log("=== INITIALIZING OPD SYSTEM ===", "SYSTEM")
        
        # Create 3 doctors with different specializations
        from models.doctor import DoctorCreate
        
        dr1 = await doctor_service.create_doctor(DoctorCreate(
            name="Dr. Rajesh Kumar",
            specialization="Cardiology",
            opd_days=["Monday", "Wednesday", "Friday"]
        ))
        
        dr2 = await doctor_service.create_doctor(DoctorCreate(
            name="Dr. Priya Sharma",
            specialization="Pediatrics",
            opd_days=["Monday", "Tuesday", "Thursday"]
        ))
        
        dr3 = await doctor_service.create_doctor(DoctorCreate(
            name="Dr. Amit Patel",
            specialization="General Medicine",
            opd_days=["Monday", "Wednesday", "Friday"]
        ))
        
        self.doctors = [dr1, dr2, dr3]
        
        self.log(f"Created doctor: {dr1.name} ({dr1.specialization})")
        self.log(f"Created doctor: {dr2.name} ({dr2.specialization})")
        self.log(f"Created doctor: {dr3.name} ({dr3.specialization})")
        
        # Create slots for today
        from models.slot import SlotCreate
        today = date.today().isoformat()
        
        time_slots = [
            {"start": "09:00", "end": "10:00", "capacity": 15},
            {"start": "10:00", "end": "11:00", "capacity": 15},
            {"start": "11:00", "end": "12:00", "capacity": 15},
            {"start": "12:00", "end": "13:00", "capacity": 10},  # Lunch - reduced
            {"start": "14:00", "end": "15:00", "capacity": 15},
            {"start": "15:00", "end": "16:00", "capacity": 15},
            {"start": "16:00", "end": "17:00", "capacity": 12},  # End of day
        ]
        
        for doctor in self.doctors:
            self.log(f"\nCreating slots for {doctor.name}:")
            for slot_data in time_slots:
                slot = await slot_service.create_slot(SlotCreate(
                    doctorId=doctor.id,
                    date=today,
                    startTime=slot_data["start"],
                    endTime=slot_data["end"],
                    maxCapacity=slot_data["capacity"]
                ))
                self.slots.append(slot)
                self.log(f"  {slot_data['start']}-{slot_data['end']} (Capacity: {slot_data['capacity']})")
        
        self.log("\n=== OPD INITIALIZATION COMPLETE ===\n", "SYSTEM")
    
    async def simulate_online_bookings(self):
        """Simulate online bookings"""
        self.log("=== SIMULATING ONLINE BOOKINGS ===", "BOOKING")
        
        from models.token import OnlineTokenCreate
        
        bookings = [
            {"doctor": 0, "slot": 0, "patient": "Ramesh Gupta", "id": "PAT001", "phone": "+919876543210"},
            {"doctor": 0, "slot": 0, "patient": "Sunita Verma", "id": "PAT002", "phone": "+919876543211"},
            {"doctor": 0, "slot": 1, "patient": "Vikram Singh", "id": "PAT003", "phone": "+919876543212"},
            {"doctor": 1, "slot": 0, "patient": "Baby Sharma", "id": "PAT004", "phone": "+919876543213"},
            {"doctor": 1, "slot": 0, "patient": "Aarav Kumar", "id": "PAT005", "phone": "+919876543214"},
            {"doctor": 1, "slot": 1, "patient": "Diya Patel", "id": "PAT006", "phone": "+919876543215"},
            {"doctor": 2, "slot": 0, "patient": "Anita Desai", "id": "PAT007", "phone": "+919876543216"},
            {"doctor": 2, "slot": 0, "patient": "Rajiv Mehta", "id": "PAT008", "phone": "+919876543217"},
            {"doctor": 2, "slot": 1, "patient": "Pooja Jain", "id": "PAT009", "phone": "+919876543218"},
            {"doctor": 0, "slot": 2, "patient": "Harish Rao", "id": "PAT010", "phone": "+919876543219"},
        ]
        
        for booking in bookings:
            slot_index = booking["doctor"] * 7 + booking["slot"]
            token = await token_service.book_online_token(OnlineTokenCreate(
                slotId=self.slots[slot_index].id,
                patientId=booking["id"],
                patientName=booking["patient"],
                phoneNumber=booking["phone"]
            ))
            self.tokens.append(token)
            self.log(f"Online booking: {booking['patient']} -> {self.doctors[booking['doctor']].name} ({token.token_number})")
        
        self.log("")
    
    async def simulate_walkins(self):
        """Simulate walk-in patients"""
        self.log("=== SIMULATING WALK-IN PATIENTS ===", "WALKIN")
        
        from models.token import WalkinTokenCreate
        
        walkins = [
            {"doctor": 0, "slot": 0, "patient": "Walk-in Patient 1", "phone": "+919876543220"},
            {"doctor": 1, "slot": 0, "patient": "Walk-in Patient 2", "phone": "+919876543221"},
            {"doctor": 2, "slot": 1, "patient": "Walk-in Patient 3", "phone": "+919876543222"},
            {"doctor": 0, "slot": 2, "patient": "Walk-in Patient 4", "phone": "+919876543223"},
            {"doctor": 1, "slot": 1, "patient": "Walk-in Patient 5", "phone": "+919876543224"},
        ]
        
        for walkin in walkins:
            slot_index = walkin["doctor"] * 7 + walkin["slot"]
            token = await token_service.generate_walkin_token(WalkinTokenCreate(
                slotId=self.slots[slot_index].id,
                patientName=walkin["patient"],
                phoneNumber=walkin["phone"]
            ))
            self.tokens.append(token)
            self.log(f"Walk-in: {walkin['patient']} -> {self.doctors[walkin['doctor']].name} ({token.token_number})")
        
        self.log("")
    
    async def simulate_priority_patients(self):
        """Simulate priority (paid) patients"""
        self.log("=== SIMULATING PRIORITY PATIENTS ===", "PRIORITY")
        
        from models.token import PriorityTokenCreate
        
        priority = [
            {"doctor": 0, "slot": 1, "patient": "VIP Patient A", "id": "VIP001", "phone": "+919876543225"},
            {"doctor": 1, "slot": 0, "patient": "VIP Patient B", "id": "VIP002", "phone": "+919876543226"},
            {"doctor": 2, "slot": 2, "patient": "VIP Patient C", "id": "VIP003", "phone": "+919876543227"},
        ]
        
        for p in priority:
            slot_index = p["doctor"] * 7 + p["slot"]
            token = await token_service.generate_priority_token(PriorityTokenCreate(
                slotId=self.slots[slot_index].id,
                patientId=p["id"],
                patientName=p["patient"],
                phoneNumber=p["phone"]
            ))
            self.tokens.append(token)
            self.log(f"Priority: {p['patient']} -> {self.doctors[p['doctor']].name} ({token.token_number}) - Moved to front!")
        
        self.log("")
    
    async def simulate_followups(self):
        """Simulate follow-up patients"""
        self.log("=== SIMULATING FOLLOW-UP PATIENTS ===", "FOLLOWUP")
        
        from models.token import FollowupTokenCreate
        
        followups = [
            {"doctor": 0, "slot": 3, "patient": "Ramesh Gupta", "id": "PAT001", "phone": "+919876543210"},
            {"doctor": 1, "slot": 2, "patient": "Baby Sharma", "id": "PAT004", "phone": "+919876543213"},
        ]
        
        for followup in followups:
            slot_index = followup["doctor"] * 7 + followup["slot"]
            token = await token_service.generate_followup_token(FollowupTokenCreate(
                slotId=self.slots[slot_index].id,
                patientId=followup["id"],
                patientName=followup["patient"],
                phoneNumber=followup["phone"]
            ))
            self.tokens.append(token)
            self.log(f"Follow-up: {followup['patient']} -> {self.doctors[followup['doctor']].name} ({token.token_number})")
        
        self.log("")
    
    async def simulate_emergencies(self):
        """Simulate emergency cases"""
        self.log("=== SIMULATING EMERGENCY CASES ===", "EMERGENCY")
        
        from models.token import EmergencyTokenCreate
        
        emergencies = [
            {"doctor": 0, "slot": 0, "patient": "Emergency Patient 1", "phone": "+919876543230"},
            {"doctor": 1, "slot": 0, "patient": "Emergency Patient 2", "phone": "+919876543231"},
        ]
        
        for emergency in emergencies:
            slot_index = emergency["doctor"] * 7 + emergency["slot"]
            token = await token_service.insert_emergency_token(EmergencyTokenCreate(
                slotId=self.slots[slot_index].id,
                patientName=emergency["patient"],
                phoneNumber=emergency["phone"]
            ))
            self.tokens.append(token)
            self.log(f"EMERGENCY: {emergency['patient']} -> {self.doctors[emergency['doctor']].name} ({token.token_number}) - PRIORITY!")
        
        self.log("")
    
    async def simulate_cancellation(self):
        """Simulate token cancellation"""
        self.log("=== SIMULATING CANCELLATION ===", "CANCEL")
        
        if len(self.tokens) > 0:
            cancel_token = self.tokens[0]
            result = await token_service.cancel_token(cancel_token.id, "Patient cancelled appointment")
            self.log(f"Cancelled: {cancel_token.patient_name} ({cancel_token.token_number})")
            self.log("Queue automatically reordered")
        
        self.log("")
    
    async def display_statistics(self):
        """Display final statistics"""
        self.log("=== FINAL STATISTICS ===", "STATS")
        
        # Count tokens by type
        from collections import Counter
        token_types = Counter([t.type for t in self.tokens])
        
        self.log(f"\nTotal Doctors: {len(self.doctors)}")
        self.log(f"Total Slots: {len(self.slots)}")
        self.log(f"Total Tokens: {len(self.tokens)}")
        self.log(f"\nTokens by Type:")
        for token_type, count in token_types.items():
            self.log(f"  {token_type}: {count}")
        
        # Show queue for first doctor's first slot
        if self.slots:
            first_slot = self.slots[0]
            queue = await token_service.get_token_queue(first_slot.id)
            self.log(f"\nQueue for {self.doctors[0].name} (09:00-10:00):")
            for token in queue[:5]:  # Show first 5
                self.log(f"  {token.token_number} - {token.patient_name} ({token.type}) - Position: {token.queue_position}")
        
        self.log("\n=== SIMULATION COMPLETE ===", "SYSTEM")
    
    async def run(self):
        """Run complete simulation"""
        try:
            await self.initialize_opd()
            await self.simulate_online_bookings()
            await self.simulate_walkins()
            await self.simulate_priority_patients()
            await self.simulate_followups()
            await self.simulate_emergencies()
            await self.simulate_cancellation()
            await self.display_statistics()
        except Exception as e:
            self.log(f"ERROR: {str(e)}", "ERROR")
            raise


async def main():
    """Main simulation entry point"""
    print("\n" + "="*60)
    print("  OPD TOKEN SYSTEM SIMULATION")
    print("  Demonstrating all features and edge cases")
    print("="*60 + "\n")
    
    # Connect to database
    await connect_db()
    
    try:
        # Run simulation
        simulation = OPDSimulation()
        await simulation.run()
    finally:
        # Disconnect from database
        await disconnect_db()
    
    print("\n" + "="*60)
    print("  SIMULATION COMPLETED SUCCESSFULLY")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
