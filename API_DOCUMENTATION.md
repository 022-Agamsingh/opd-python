# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, implement JWT tokens or API keys.

## Response Format

All responses follow this format:

```json
{
  "success": true,
  "message": "Optional message",
  "data": {},
  "count": 0 // For list responses
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error message",
  "detail": "Detailed error information"
}
```

## Doctor Endpoints

### Create Doctor

**POST** `/api/doctors`

Create a new doctor in the system.

**Request Body:**

```json
{
  "name": "Dr. Rajesh Kumar",
  "specialization": "Cardiology",
  "opd_days": ["Monday", "Wednesday", "Friday"]
}
```

**Response:** `201 Created`

```json
{
  "success": true,
  "message": "Doctor created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Dr. Rajesh Kumar",
    "specialization": "Cardiology",
    "opd_days": ["Monday", "Wednesday", "Friday"],
    "created_at": "2024-01-15T10:00:00"
  }
}
```

### Get All Doctors

**GET** `/api/doctors`

Get all doctors or filter by specialization.

**Query Parameters:**

- `specialization` (optional): Filter by specialization

**Response:** `200 OK`

```json
{
  "success": true,
  "count": 3,
  "data": [
    {
      "id": "doctor-1",
      "name": "Dr. Rajesh Kumar",
      "specialization": "Cardiology",
      "opd_days": ["Monday", "Wednesday", "Friday"]
    }
  ]
}
```

### Get Doctor by ID

**GET** `/api/doctors/{doctor_id}`

Get a specific doctor by ID.

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "id": "doctor-1",
    "name": "Dr. Rajesh Kumar",
    "specialization": "Cardiology",
    "opd_days": ["Monday", "Wednesday", "Friday"]
  }
}
```

---

## Slot Endpoints

### Create Slot

**POST** `/api/slots`

Create a new time slot for a doctor.

**Request Body:**

```json
{
  "doctorId": "doctor-1",
  "date": "2024-01-15",
  "startTime": "09:00",
  "endTime": "10:00",
  "maxCapacity": 20
}
```

**Response:** `201 Created`

```json
{
  "success": true,
  "message": "Slot created successfully",
  "data": {
    "id": "slot-1",
    "doctorId": "doctor-1",
    "date": "2024-01-15",
    "startTime": "09:00",
    "endTime": "10:00",
    "maxCapacity": 20,
    "currentCount": 0,
    "availableCapacity": 20,
    "isFull": false,
    "status": "ACTIVE"
  }
}
```

### Get Slot by ID

**GET** `/api/slots/{slot_id}`

Get a specific slot by ID.

**Response:** `200 OK`

### Get Slots by Doctor

**GET** `/api/slots/doctor/{doctor_id}`

Get all slots for a specific doctor.

**Query Parameters:**

- `date` (optional): Filter by specific date (YYYY-MM-DD)

**Response:** `200 OK`

```json
{
  "success": true,
  "count": 7,
  "data": [
    {
      "id": "slot-1",
      "doctorId": "doctor-1",
      "date": "2024-01-15",
      "startTime": "09:00",
      "endTime": "10:00",
      "maxCapacity": 20,
      "currentCount": 5,
      "availableCapacity": 15,
      "isFull": false
    }
  ]
}
```

### Get Available Slots

**GET** `/api/slots/doctor/{doctor_id}/available`

Get available (not full) slots for a doctor.

**Query Parameters:**

- `date` (optional): Filter by specific date

**Response:** `200 OK`

### Mark Slot Delayed

**PATCH** `/api/slots/{slot_id}/delay`

Mark a slot as delayed.

**Query Parameters:**

- `delay_minutes` (required): Number of minutes delayed

**Response:** `200 OK`

```json
{
  "success": true,
  "message": "Slot marked as delayed by 30 minutes",
  "data": {
    "id": "slot-1",
    "isDelayed": true,
    "delayMinutes": 30,
    "status": "DELAYED"
  }
}
```

### Get Slot Statistics

**GET** `/api/slots/{slot_id}/stats`

Get statistics for a specific slot.

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "slotId": "slot-1",
    "maxCapacity": 20,
    "currentCount": 15,
    "availableCapacity": 5,
    "isFull": false,
    "tokenStats": {
      "PENDING": 10,
      "CHECKED_IN": 3,
      "COMPLETED": 2
    }
  }
}
```

---

## Token Endpoints

### Book Online Token

**POST** `/api/tokens/book`

Book an online appointment token.

**Request Body:**

```json
{
  "slotId": "slot-1",
  "patientId": "PAT001",
  "patientName": "Ramesh Gupta",
  "phoneNumber": "+919876543210"
}
```

**Response:** `201 Created`

```json
{
  "success": true,
  "message": "Token booked successfully",
  "data": {
    "id": "token-1",
    "tokenNumber": "T001",
    "patientId": "PAT001",
    "patientName": "Ramesh Gupta",
    "slotId": "slot-1",
    "type": "ONLINE",
    "priority": 200,
    "queuePosition": 1,
    "estimatedTime": "2024-01-15T09:00:00",
    "status": "PENDING",
    "phoneNumber": "+919876543210"
  }
}
```

### Generate Walk-in Token

**POST** `/api/tokens/walkin`

Generate a walk-in token for a patient.

**Request Body:**

```json
{
  "slotId": "slot-1",
  "patientName": "Walk-in Patient",
  "phoneNumber": "+919876543211"
}
```

**Response:** `201 Created`

### Generate Priority Token

**POST** `/api/tokens/priority`

Generate a priority (paid) token.

**Request Body:**

```json
{
  "slotId": "slot-1",
  "patientId": "VIP001",
  "patientName": "VIP Patient",
  "phoneNumber": "+919876543212"
}
```

**Response:** `201 Created`

- Priority patients get higher queue position
- Priority score: 500 (vs 200 for online, 100 for walk-in)

### Generate Follow-up Token

**POST** `/api/tokens/followup`

Generate a follow-up token for returning patient.

**Request Body:**

```json
{
  "slotId": "slot-1",
  "patientId": "PAT001",
  "patientName": "Ramesh Gupta",
  "phoneNumber": "+919876543210"
}
```

**Response:** `201 Created`

- Priority score: 300 (medium priority)

### Insert Emergency Token

**POST** `/api/tokens/emergency`

Insert an emergency token (highest priority).

**Request Body:**

```json
{
  "slotId": "slot-1",
  "patientName": "Emergency Patient",
  "phoneNumber": "+919876543213"
}
```

**Response:** `201 Created`

- Priority score: 1000 (highest)
- Automatically moved to position 1
- If slot is full, capacity is extended by 1

### Get Token by ID

**GET** `/api/tokens/{token_id}`

Get a specific token by ID.

**Response:** `200 OK`

### Get Tokens by Patient

**GET** `/api/tokens/patient/{patient_id}`

Get all tokens for a specific patient.

**Response:** `200 OK`

```json
{
  "success": true,
  "count": 3,
  "data": [
    {
      "id": "token-1",
      "tokenNumber": "T001",
      "patientId": "PAT001",
      "patientName": "Ramesh Gupta",
      "type": "ONLINE",
      "status": "COMPLETED"
    }
  ]
}
```

### Get Token Queue

**GET** `/api/tokens/queue/{slot_id}`

Get the current queue for a slot (sorted by position).

**Response:** `200 OK`

```json
{
  "success": true,
  "count": 5,
  "data": [
    {
      "tokenNumber": "T001",
      "patientName": "Emergency Patient",
      "type": "EMERGENCY",
      "queuePosition": 1,
      "priority": 1000,
      "estimatedTime": "2024-01-15T09:00:00"
    },
    {
      "tokenNumber": "T002",
      "patientName": "VIP Patient",
      "type": "PRIORITY",
      "queuePosition": 2,
      "priority": 500,
      "estimatedTime": "2024-01-15T09:10:00"
    }
  ]
}
```

### Update Token Status

**PATCH** `/api/tokens/{token_id}/status`

Update the status of a token.

**Request Body:**

```json
{
  "status": "CHECKED_IN"
}
```

**Valid Statuses:**

- `PENDING`: Token created, patient not arrived
- `CHECKED_IN`: Patient arrived and checked in
- `CONSULTING`: Patient currently with doctor
- `COMPLETED`: Consultation finished
- `CANCELLED`: Appointment cancelled
- `NO_SHOW`: Patient didn't show up

**Response:** `200 OK`

### Cancel Token

**DELETE** `/api/tokens/{token_id}/cancel`

Cancel a token and reorder the queue.

**Request Body:**

```json
{
  "reason": "Patient cancelled appointment"
}
```

**Response:** `200 OK`

```json
{
  "success": true,
  "message": "Token cancelled successfully and queue reordered",
  "data": {
    "tokenId": "token-1",
    "status": "cancelled",
    "reason": "Patient cancelled appointment"
  }
}
```

### Reallocate Tokens

**POST** `/api/tokens/reallocate/{slot_id}`

Reallocate all pending tokens from one slot to another.

**Request Body:**

```json
{
  "target_slot_id": "slot-2"
}
```

**Response:** `200 OK`

```json
{
  "success": true,
  "message": "Tokens reallocated successfully",
  "data": {
    "reallocated": 5,
    "sourceSlot": "slot-1",
    "targetSlot": "slot-2"
  }
}
```

---

## Error Codes

| Code | Description                    |
| ---- | ------------------------------ |
| 200  | Success                        |
| 201  | Created successfully           |
| 400  | Bad request (validation error) |
| 404  | Resource not found             |
| 500  | Internal server error          |

---

## Priority System

Token types and their priority scores:

| Type      | Priority Score | Description                         |
| --------- | -------------- | ----------------------------------- |
| EMERGENCY | 1000           | Critical cases, immediate attention |
| PRIORITY  | 500            | Paid priority service               |
| FOLLOWUP  | 300            | Follow-up appointments              |
| ONLINE    | 200            | Pre-booked online                   |
| WALKIN    | 100            | Walk-in patients                    |

---

## Rate Limiting

Currently no rate limiting. In production, implement:

- 100 requests per minute per IP
- 1000 requests per hour per IP

---

## WebSocket Support (Future)

Real-time queue updates via WebSocket:

```javascript
ws://localhost:8000/ws/queue/{slot_id}
```

Will broadcast:

- New token added
- Token status changed
- Queue reordered
- Slot delayed
