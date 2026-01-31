# Development Notes

## Things to Remember

### Priority System

- EMERGENCY: 1000 (critical cases, bypass queue)
- PRIORITY: 500 (paid/senior citizens)
- FOLLOWUP: 300 (returning patients)
- ONLINE: 200 (pre-booked)
- WALKIN: 100 (same-day)

### Common Issues I've Fixed

1. **Pydantic v2 model immutability**: Use `model_copy()` instead of direct assignment
2. **Alias vs attribute names**: MongoDB uses camelCase, Python uses snake_case
3. **Async database calls**: Always use `await` with Motor operations
4. **Time format**: Stick to "HH:MM" format for consistency

### Useful Commands

```bash
# Start server with auto-reload
python main.py

# Run tests
python test_basic.py

# Run simulation
python simulation.py

# Check MongoDB connection
python -c "from pymongo import MongoClient; print(MongoClient().server_info())"

# Install new package
pip install package_name && pip freeze > requirements.txt
```

### API Endpoints Worth Testing

- POST /api/tokens/book - Online booking
- POST /api/tokens/emergency - Emergency allocation (watch it bypass queue!)
- GET /api/tokens/queue/{slotId} - See queue ordering
- POST /api/tokens/reallocate/{slotId} - Force reallocation

### MongoDB Collections

- doctors: Doctor profiles and OPD schedules
- slots: Time slots with capacity tracking
- tokens: Patient tokens with queue positions

### Future Improvements

- [ ] Add WebSocket for real-time queue updates
- [ ] Implement SMS notifications for token status
- [ ] Add doctor dashboard with analytics
- [ ] Patient mobile app integration
- [ ] Waiting time prediction ML model
- [ ] Multi-hospital support
- [ ] Appointment reminder system

### Performance Notes

- Database indexes created on startup (see database.py)
- Async operations throughout for better concurrency
- Token reallocation can be expensive with large queues (optimize later?)

## Debugging Tips

If priority ordering seems wrong:

1. Check DEBUG flag in token_service.py
2. Verify PRIORITY_WEIGHTS in config.py
3. Look at the priority score calculation (base + time_factor)

If tokens aren't saving:

1. Check MongoDB connection in .env
2. Verify db instance is initialized
3. Look for validation errors in Pydantic models

## Testing Strategy

1. Basic tests: `test_basic.py` (no DB needed)
2. Integration: Use `simulation.py` with real MongoDB
3. API testing: Use Swagger UI at http://localhost:8000/docs

---

Last updated: January 2026
