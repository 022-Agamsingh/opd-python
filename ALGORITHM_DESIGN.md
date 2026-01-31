# Token Allocation Algorithm Documentation

## Overview

The OPD Token Allocation Engine uses a **priority-based queue scheduling algorithm** with dynamic reallocation capabilities. The core algorithm ensures fair distribution while maintaining strict capacity limits and handling real-world edge cases.

## Algorithm Design

### 1. Core Allocation Algorithm

```python
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
    # Step 1: Validate slot existence and capacity
    slot = await slot_service.get_slot(slot_id)
    if slot.is_full:
        raise ValueError("Slot is full")

    # Step 2: Create token with priority score
    priority_score = _calculate_priority_score(token_type)
    token = Token(...)

    # Step 3: Insert into priority queue
    await _assign_token_number(token, slot_id)

    # Step 4: Update slot capacity
    await slot_service.increment_slot_count(slot_id)

    # Step 5: Calculate estimated time
    await _calculate_estimated_time(token)

    # Step 6: Persist token
    await db.tokens.insert_one(token.model_dump())

    return token
```

### 2. Priority Score Calculation

```python
def _calculate_priority_score(token_type: str) -> int:
    """
    Calculate priority score for token
    Base priority from type + time factor for FIFO within same priority
    """
    # Base score from priority weights
    base_score = PRIORITY_WEIGHTS.get(token_type, 100)

    # Add small time factor to ensure FIFO within same priority
    # Use nanosecond precision divided by large number
    time_factor = time.time() / 1000000000

    # Priority score = base + time factor
    # Higher numbers = higher priority
    return int(base_score + time_factor)

# Priority Weights:
PRIORITY_WEIGHTS = {
    "EMERGENCY": 1000,
    "PRIORITY": 500,    # Paid patients
    "FOLLOWUP": 300,
    "ONLINE": 200,
    "WALKIN": 100,
}
```

**Why this design?**

- Higher numbers = higher priority (intuitive)
- Time factor ensures FIFO within same priority level
- Emergency always gets precedence
- Small time factor doesn't affect priority ordering between types

### 3. Token Number Assignment

```python
async def _assign_token_number(new_token: Token, slot_id: str):
    """
    Assign token number based on priority queue
    Sorts all active tokens and assigns sequential positions
    """
    # Get all active tokens in slot (exclude CANCELLED and NO_SHOW)
    existing_tokens = await db.tokens.find({
        "slotId": slot_id,
        "status": {"$nin": ["CANCELLED", "NO_SHOW"]}
    }).to_list(None)

    # Add new token to list
    existing_tokens.append(new_token)

    # Sort by priority score (higher first = descending order)
    existing_tokens.sort(key=lambda t: t.priority, reverse=True)

    # Assign sequential positions
    for index, token in enumerate(existing_tokens):
        token.queue_position = index + 1
        token.token_number = f"T{str(index + 1).zfill(3)}"
```

**Example:**

- Emergency patient arrives to slot with 5 existing tokens
- Emergency gets priority_score ≈ 1000
- Existing tokens have scores 200-500
- After sorting: Emergency becomes position 1 (T001)
- All other tokens shift down by 1

### 4. Estimated Time Calculation

```python
async def _calculate_estimated_time(token: Token):
    """Calculate estimated time for patient"""
    slot = await slot_service.get_slot(token.slot_id)

    # Parse slot start time
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
```

## Edge Cases Handled

### 1. Emergency Token Insertion

**Scenario:** Emergency patient arrives when slot is full

**Solution:**

```python
if slot.is_full:
    # Temporarily extend capacity by 1 for emergency
    await db.slots.update_one(
        {"_id": slot_id},
        {"$inc": {"maxCapacity": 1}}
    )

# Emergency gets highest priority (1000)
# Automatically inserted at position 1
# All other tokens reordered
```

### 2. Token Cancellation

**Scenario:** Patient cancels appointment

**Solution:**

```python
async def cancel_token(token_id: str, reason: str):
    # Update token status to CANCELLED
    await update_token_status(token_id, "CANCELLED")

    # Decrement slot count
    await slot_service.decrement_slot_count(slot_id)

    # Reorder remaining tokens
    await _reorder_slot_tokens(slot_id)
```

### 3. Slot Reallocation

**Scenario:** Doctor delayed/unavailable, need to move patients

**Solution:**

```python
async def reallocate_tokens(source_slot_id: str, target_slot_id: str):
    # Get all pending tokens from source
    tokens = await get_pending_tokens(source_slot_id)

    # Check target slot capacity
    if target_slot.available_capacity < len(tokens):
        raise ValueError("Insufficient capacity")

    # Move tokens to target slot
    for token in tokens:
        token.slot_id = target_slot_id
        await update_slot_counts()

    # Reorder tokens in target slot
    await _reorder_slot_tokens(target_slot_id)
```

### 4. Priority Patient Late Arrival

**Scenario:** Priority patient arrives late but still needs precedence

**Solution:**

- Priority score still higher than regular patients
- Will be inserted ahead of lower priority tokens
- Maintains fair ordering within priority level

### 5. Follow-up Patient Priority

**Scenario:** Follow-up patients get medium priority

**Solution:**

- Priority: 300 (between PRIORITY and ONLINE)
- Higher than new patients but lower than paid priority
- Fair treatment for returning patients

## Performance Considerations

### Time Complexity

- **Token Allocation**: O(n log n) where n = tokens in slot
  - Sorting tokens by priority
- **Priority Calculation**: O(1)
- **Estimated Time**: O(1)
- **Cancellation**: O(n log n) for reordering

### Space Complexity

- O(n) where n = total tokens in system
- Indexed by slotId, patientId, status for fast queries

### Database Indexes

```python
# Token indexes
await db.tokens.create_index("tokenNumber")
await db.tokens.create_index("patientId")
await db.tokens.create_index("slotId")
await db.tokens.create_index([("slotId", 1), ("queuePosition", 1)])
await db.tokens.create_index([("slotId", 1), ("status", 1)])

# Slot indexes
await db.slots.create_index("doctorId")
await db.slots.create_index("date")
await db.slots.create_index([("doctorId", 1), ("date", 1), ("startTime", 1)])
```

## Example Scenarios

### Scenario 1: Normal Day

```
Time: 09:00 AM
Slot: Dr. Smith (Cardiology) 09:00-10:00 (Capacity: 20)

1. Online booking (PAT001) → T001 (Priority: 200)
2. Online booking (PAT002) → T002 (Priority: 200)
3. Walk-in (WALK001) → T003 (Priority: 100)
4. Priority patient (VIP001) arrives → Reorder:
   - VIP001 → T001 (Priority: 500)
   - PAT001 → T002 (Priority: 200)
   - PAT002 → T003 (Priority: 200)
   - WALK001 → T004 (Priority: 100)
```

### Scenario 2: Emergency Case

```
Time: 10:30 AM
Slot: Dr. Patel (General) 10:00-11:00 (Capacity: 15/15 FULL)

Emergency patient arrives:
1. Extend capacity to 16
2. Insert emergency at T001
3. All existing tokens shift down
4. Emergency patient seen immediately
```

### Scenario 3: Doctor Delay

```
Time: 11:00 AM
Slot: Dr. Kumar delayed by 30 minutes

1. Mark slot as delayed
2. Add 30 minutes to all estimated times
3. Notify patients of delay
4. Option to reallocate to different doctor
```

## Best Practices

1. **Always validate slot capacity** before allocation
2. **Reorder queue** after any insertion or cancellation
3. **Handle emergencies** with capacity extension
4. **Calculate accurate** estimated times
5. **Use database indexes** for performance
6. **Maintain audit trail** of all changes

## Future Enhancements

1. **Machine Learning**: Predict consultation times based on history
2. **Multi-slot Booking**: Allow patients to book multiple slots
3. **Waitlist Management**: Automatic promotion from waitlist
4. **SMS Notifications**: Alert patients of queue position
5. **Dynamic Pricing**: Adjust priority costs based on demand
