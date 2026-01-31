"""
Demo server - runs without MongoDB for testing API structure
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI(
    title="OPD Token Allocation Engine - DEMO",
    description="Hospital OPD Token Allocation System (Demo Mode - No Database)",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "OPD Token Allocation Engine API - DEMO MODE",
        "version": "1.0.0",
        "status": "Running without database",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "demo_data": "/demo",
        },
        "note": "This is a demo. To use full features, ensure MongoDB is running and use main.py"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "OK",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "OPD Token Allocation Engine",
        "mode": "DEMO"
    }


@app.get("/demo")
async def demo_data():
    """Show demo data structure"""
    return {
        "success": True,
        "demo": {
            "doctor": {
                "id": "doc-123",
                "name": "Dr. Rajesh Kumar",
                "specialization": "Cardiology",
                "opd_days": ["Monday", "Wednesday", "Friday"]
            },
            "slot": {
                "id": "slot-456",
                "doctorId": "doc-123",
                "date": "2024-01-15",
                "startTime": "09:00",
                "endTime": "10:00",
                "maxCapacity": 20,
                "currentCount": 5,
                "availableCapacity": 15,
                "isFull": False
            },
            "tokens": [
                {
                    "tokenNumber": "T001",
                    "patientName": "Emergency Patient",
                    "type": "EMERGENCY",
                    "priority": 1000,
                    "queuePosition": 1,
                    "estimatedTime": "2024-01-15T09:00:00"
                },
                {
                    "tokenNumber": "T002",
                    "patientName": "Priority Patient",
                    "type": "PRIORITY",
                    "priority": 500,
                    "queuePosition": 2,
                    "estimatedTime": "2024-01-15T09:10:00"
                },
                {
                    "tokenNumber": "T003",
                    "patientName": "Online Patient",
                    "type": "ONLINE",
                    "priority": 200,
                    "queuePosition": 3,
                    "estimatedTime": "2024-01-15T09:20:00"
                }
            ]
        },
        "priority_system": {
            "EMERGENCY": 1000,
            "PRIORITY": 500,
            "FOLLOWUP": 300,
            "ONLINE": 200,
            "WALKIN": 100
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("  OPD TOKEN SYSTEM - DEMO MODE")
    print("  Running without database connection")
    print("="*60)
    print("\nStarting server...")
    print("Visit: http://localhost:8000")
    print("Docs:  http://localhost:8000/docs\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
