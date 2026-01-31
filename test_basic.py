"""
Quick test script for OPD Token System
Tests the models and basic functionality without requiring MongoDB
"""
import sys
from datetime import datetime, date


def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    try:
        from models.doctor import Doctor, DoctorCreate
        from models.slot import Slot, SlotCreate
        from models.token import Token, OnlineTokenCreate
        from config import settings, PRIORITY_WEIGHTS, TOKEN_TYPES
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_models():
    """Test model creation and validation"""
    print("\nTesting models...")
    try:
        from models.doctor import DoctorCreate
        from models.slot import SlotCreate
        from models.token import OnlineTokenCreate
        
        # Test Doctor
        doctor_data = DoctorCreate(
            name="Dr. Test",
            specialization="Testing",
            opd_days=["Monday", "Tuesday"]
        )
        print(f"✓ Doctor model: {doctor_data.name}")
        
        # Test Slot
        slot_data = SlotCreate(
            doctorId="test-doctor-id",
            date=date.today().isoformat(),
            startTime="09:00",
            endTime="10:00",
            maxCapacity=20
        )
        print(f"✓ Slot model: {slot_data.start_time}-{slot_data.end_time}")
        
        # Test Token
        token_data = OnlineTokenCreate(
            slotId="test-slot-id",
            patientId="PAT001",
            patientName="Test Patient",
            phoneNumber="+1234567890"
        )
        print(f"✓ Token model: {token_data.patient_name}")
        
        return True
    except Exception as e:
        print(f"✗ Model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_priority_calculation():
    """Test priority score calculation"""
    print("\nTesting priority calculation...")
    try:
        from config import PRIORITY_WEIGHTS
        import time
        
        # Test priority weights
        print(f"  EMERGENCY: {PRIORITY_WEIGHTS['EMERGENCY']}")
        print(f"  PRIORITY: {PRIORITY_WEIGHTS['PRIORITY']}")
        print(f"  FOLLOWUP: {PRIORITY_WEIGHTS['FOLLOWUP']}")
        print(f"  ONLINE: {PRIORITY_WEIGHTS['ONLINE']}")
        print(f"  WALKIN: {PRIORITY_WEIGHTS['WALKIN']}")
        
        # Simulate priority calculation
        def calculate_priority(token_type):
            base_score = PRIORITY_WEIGHTS.get(token_type, 100)
            time_factor = time.time() / 1000000000
            return int(base_score + time_factor)
        
        emergency_score = calculate_priority("EMERGENCY")
        online_score = calculate_priority("ONLINE")
        walkin_score = calculate_priority("WALKIN")
        
        print(f"\n  Emergency score: {emergency_score}")
        print(f"  Online score: {online_score}")
        print(f"  Walk-in score: {walkin_score}")
        
        assert emergency_score > online_score > walkin_score, "Priority ordering incorrect"
        print("✓ Priority calculation working correctly")
        
        return True
    except Exception as e:
        print(f"✗ Priority calculation failed: {e}")
        return False


def test_token_queue_ordering():
    """Test token queue ordering logic"""
    print("\nTesting token queue ordering...")
    try:
        from models.token import Token
        from config import PRIORITY_WEIGHTS
        import time
        
        # Create sample tokens
        tokens = []
        
        # Online booking
        token1 = Token(
            _id="token-1",
            tokenNumber="T000",
            patientId="PAT001",
            patientName="Online Patient",
            slotId="slot-1",
            type="ONLINE",
            priority=PRIORITY_WEIGHTS["ONLINE"],
            queuePosition=0,
            estimatedTime=datetime.now().isoformat()
        )
        tokens.append(token1)
        
        # Walk-in
        token2 = Token(
            _id="token-2",
            tokenNumber="T000",
            patientId="WALK-001",
            patientName="Walk-in Patient",
            slotId="slot-1",
            type="WALKIN",
            priority=PRIORITY_WEIGHTS["WALKIN"],
            queuePosition=0,
            estimatedTime=datetime.now().isoformat()
        )
        tokens.append(token2)
        
        # Emergency
        token3 = Token(
            _id="token-3",
            tokenNumber="T000",
            patientId="EMRG-001",
            patientName="Emergency Patient",
            slotId="slot-1",
            type="EMERGENCY",
            priority=PRIORITY_WEIGHTS["EMERGENCY"],
            queuePosition=0,
            estimatedTime=datetime.now().isoformat()
        )
        tokens.append(token3)
        
        # Sort by priority (highest first)
        tokens.sort(key=lambda t: t.priority, reverse=True)
        
        # Create new tokens with updated positions (Pydantic models are immutable)
        sorted_tokens = []
        for index, token in enumerate(tokens):
            # Create new token with updated values
            updated_token = token.model_copy(update={
                "queue_position": index + 1,
                "token_number": f"T{str(index + 1).zfill(3)}"
            })
            sorted_tokens.append(updated_token)
        
        tokens = sorted_tokens
        
        print("\nQueue order after sorting:")
        for token in tokens:
            print(f"  {token.token_number}: {token.patient_name} ({token.type}) - Priority: {token.priority}")
        
        # Verify order
        assert tokens[0].type == "EMERGENCY", "Emergency should be first"
        assert tokens[1].type == "ONLINE", "Online should be second"
        assert tokens[2].type == "WALKIN", "Walk-in should be third"
        
        print("✓ Queue ordering working correctly")
        return True
    except Exception as e:
        print(f"✗ Queue ordering failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from config import settings
        
        print(f"  Port: {settings.PORT}")
        print(f"  Environment: {settings.ENVIRONMENT}")
        print(f"  MongoDB URI: {settings.MONGODB_URI}")
        print(f"  Default slot duration: {settings.DEFAULT_SLOT_DURATION} min")
        print(f"  Default max capacity: {settings.DEFAULT_MAX_CAPACITY}")
        
        print("✓ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("OPD TOKEN SYSTEM - QUICK TEST")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Models", test_models()))
    results.append(("Configuration", test_configuration()))
    results.append(("Priority Calculation", test_priority_calculation()))
    results.append(("Queue Ordering", test_token_queue_ordering()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:30} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The OPD system is working correctly.")
        print("\nNext steps:")
        print("1. Ensure MongoDB is running (locally or use MongoDB Atlas)")
        print("2. Run: python main.py (to start the API server)")
        print("3. Visit: http://localhost:8000/docs (for interactive API docs)")
        print("4. Run: python simulation.py (for complete simulation)")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
