# OPD Token Allocation Engine - Python

A sophisticated token allocation system for hospital Out-Patient Department (OPD) that supports elastic capacity management, dynamic reallocation, and priority-based queuing.

**Python Implementation using FastAPI, Motor (async MongoDB), and Pydantic**

## 🏥 Features

- **Multi-source Token Generation**: Online booking, Walk-in, Priority (Paid), Follow-up, Emergency
- **Dynamic Priority System**: Automatic token ordering based on priority scores
- **Elastic Capacity Management**: Handles slot delays, cancellations, and emergency insertions
- **Real-time Reallocation**: Automatically redistributes tokens when conditions change
- **Edge Case Handling**: No-shows, cancellations, doctor delays, emergency cases
- **Comprehensive API**: RESTful endpoints for all operations with FastAPI
- **Async/Await**: Fully asynchronous for high performance
- **Interactive Documentation**: Auto-generated API docs with Swagger UI

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or cloud instance)
- pip or poetry for package management

### Installation

```bash
# Navigate to project directory
cd opd-python

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env file with your MongoDB URI
# MONGODB_URI=mongodb://localhost:27017/opd_token_system
```

### Start the Server

```bash
# Development mode with auto-reload
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --port 8000
```

The server will start on `http://localhost:8000`

### Run Simulation

```bash
# Run complete OPD day simulation
python simulation.py
```

This will simulate a complete OPD day with 3 doctors, demonstrating all features and edge cases.

### View Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### Doctors

| Method | Endpoint                                 | Description              |
| ------ | ---------------------------------------- | ------------------------ |
| POST   | `/api/doctors`                           | Create a new doctor      |
| GET    | `/api/doctors`                           | Get all doctors          |
| GET    | `/api/doctors/{id}`                      | Get doctor by ID         |
| GET    | `/api/doctors?specialization=Cardiology` | Filter by specialization |

### Slots

| Method | Endpoint                                                 | Description                |
| ------ | -------------------------------------------------------- | -------------------------- |
| POST   | `/api/slots`                                             | Create a new slot          |
| GET    | `/api/slots/{id}`                                        | Get slot by ID             |
| GET    | `/api/slots/doctor/{doctorId}`                           | Get all slots for a doctor |
| GET    | `/api/slots/doctor/{doctorId}/available?date=YYYY-MM-DD` | Get available slots        |
| PATCH  | `/api/slots/{id}/delay?delay_minutes=30`                 | Mark slot as delayed       |
| GET    | `/api/slots/{id}/stats`                                  | Get slot statistics        |

### Tokens

| Method | Endpoint                          | Description                    |
| ------ | --------------------------------- | ------------------------------ |
| POST   | `/api/tokens/book`                | Book an online token           |
| POST   | `/api/tokens/walkin`              | Generate walk-in token         |
| POST   | `/api/tokens/priority`            | Generate priority (paid) token |
| POST   | `/api/tokens/followup`            | Generate follow-up token       |
| POST   | `/api/tokens/emergency`           | Insert emergency token         |
| GET    | `/api/tokens/{id}`                | Get token by ID                |
| GET    | `/api/tokens/patient/{patientId}` | Get all tokens for a patient   |
| GET    | `/api/tokens/queue/{slotId}`      | Get token queue for a slot     |
| PATCH  | `/api/tokens/{id}/status`         | Update token status            |
| DELETE | `/api/tokens/{id}/cancel`         | Cancel a token                 |
| POST   | `/api/tokens/reallocate/{slotId}` | Reallocate tokens from a slot  |

## 📝 API Usage Examples

### 1. Create a Doctor

```bash
curl -X POST http://localhost:8000/api/doctors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Smith",
    "specialization": "Cardiology",
    "opd_days": ["Monday", "Wednesday", "Friday"]
  }'
```

### 2. Create a Slot

```bash
curl -X POST http://localhost:8000/api/slots \
  -H "Content-Type: application/json" \
  -d '{
    "doctorId": "doctor-uuid-here",
    "date": "2024-01-15",
    "startTime": "09:00",
    "endTime": "10:00",
    "maxCapacity": 20
  }'
```

### 3. Book an Online Token

```bash
curl -X POST http://localhost:8000/api/tokens/book \
  -H "Content-Type: application/json" \
  -d '{
    "slotId": "slot-uuid-here",
    "patientId": "PAT001",
    "patientName": "John Doe",
    "phoneNumber": "+1234567890"
  }'
```

### 4. Generate Walk-in Token

```bash
curl -X POST http://localhost:8000/api/tokens/walkin \
  -H "Content-Type: application/json" \
  -d '{
    "slotId": "slot-uuid-here",
    "patientName": "Jane Smith",
    "phoneNumber": "+0987654321"
  }'
```

### 5. Insert Emergency Token

```bash
curl -X POST http://localhost:8000/api/tokens/emergency \
  -H "Content-Type: application/json" \
  -d '{
    "slotId": "slot-uuid-here",
    "patientName": "Emergency Patient",
    "phoneNumber": "+1122334455"
  }'
```

### 6. Get Token Queue

```bash
curl http://localhost:8000/api/tokens/queue/slot-uuid-here
```

### 7. Cancel a Token

```bash
curl -X DELETE http://localhost:8000/api/tokens/token-uuid-here/cancel \
  -H "Content-Type: application/json" \
  -d '{"reason": "Patient cancelled"}'
```

## 🔧 Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Motor**: Async MongoDB driver for Python
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running FastAPI applications
- **Python 3.8+**: Async/await syntax for concurrent operations

## 🏗️ Project Structure

```
opd-python/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration and settings
├── database.py             # MongoDB connection and setup
├── simulation.py           # OPD simulation script
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore patterns
├── models/                # Pydantic models
│   ├── __init__.py
│   ├── doctor.py          # Doctor models
│   ├── slot.py            # Slot models
│   └── token.py           # Token models
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── doctor_service.py  # Doctor service
│   ├── slot_service.py    # Slot service
│   └── token_service.py   # Token service (core algorithm)
└── routes/                # API routes
    ├── __init__.py
    ├── doctor_routes.py   # Doctor endpoints
    ├── slot_routes.py     # Slot endpoints
    └── token_routes.py    # Token endpoints
```

## 🧮 Core Algorithm

The system uses a **priority-based queue scheduling algorithm** with dynamic reallocation:

### Priority Calculation

```python
def _calculate_priority_score(token_type: str) -> int:
    base_score = PRIORITY_WEIGHTS.get(token_type, 100)
    time_factor = time.time() / 1000000000
    return int(base_score + time_factor)

# Priority Weights:
# EMERGENCY: 1000
# PRIORITY:  500
# FOLLOWUP:  300
# ONLINE:    200
# WALKIN:    100
```

### Token Assignment

1. Calculate priority score based on token type
2. Add new token to existing queue
3. Sort all tokens by priority (descending)
4. Assign sequential positions (T001, T002, etc.)
5. Calculate estimated consultation time

### Emergency Handling

- Emergency tokens get highest priority (1000)
- If slot is full, temporarily extend capacity by 1
- Automatically reorder entire queue
- All lower-priority tokens shift down

## 🔐 Environment Variables

```env
# Server Configuration
PORT=8000
ENVIRONMENT=development

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/opd_token_system

# Slot Configuration
DEFAULT_SLOT_DURATION=10
DEFAULT_MAX_CAPACITY=6

# Priority Weights
EMERGENCY_PRIORITY=1000
PAID_PRIORITY=500
FOLLOWUP_PRIORITY=300
ONLINE_PRIORITY=200
WALKIN_PRIORITY=100

# Timeout Configuration
NO_SHOW_TIMEOUT=15
LATE_ARRIVAL_GRACE=10
```

## 🧪 Testing

Run the simulation to test all features:

```bash
python simulation.py
```

This will:

- Create 3 doctors with different specializations
- Create 7 time slots for each doctor (9 AM - 5 PM)
- Simulate 10 online bookings
- Simulate 5 walk-in patients
- Simulate 3 priority (paid) patients
- Simulate 2 follow-up patients
- Simulate 2 emergency cases
- Demonstrate token cancellation
- Display final statistics

## 📊 Features Demonstration

### 1. Priority-based Ordering

```python
# Online booking (priority: 200)
# Walk-in (priority: 100)
# Priority patient arrives (priority: 500)
# Result: Priority patient moves to front, others shift down
```

### 2. Emergency Insertion

```python
# Slot has 15/15 patients (full)
# Emergency patient arrives (priority: 1000)
# System extends capacity to 16/16
# Emergency patient gets position 1
# All other patients reordered
```

### 3. Dynamic Reallocation

```python
# Doctor delayed or slot cancelled
# Reallocate all pending tokens to another slot
# Maintain priority order in new slot
```

## 🎯 Comparison with Node.js Version

| Feature       | Node.js              | Python                   |
| ------------- | -------------------- | ------------------------ |
| Framework     | Express              | FastAPI                  |
| Database      | Mongoose             | Motor (async)            |
| Validation    | express-validator    | Pydantic                 |
| Async Support | Promises/async-await | async/await              |
| API Docs      | Manual               | Auto-generated (Swagger) |
| Type Safety   | JSDoc                | Type hints + Pydantic    |
| Performance   | High                 | High (async)             |

## 📄 License

MIT

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions, please open an issue on the GitHub repository.
#   o p d - p y t h o n  
 