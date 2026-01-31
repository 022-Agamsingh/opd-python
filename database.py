"""Database connection module"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection manager"""
    
    client: AsyncIOMotorClient = None
    db = None


db_instance = Database()


async def connect_db():
    """Connect to MongoDB"""
    try:
        # Initialize async MongoDB client
        db_instance.client = AsyncIOMotorClient(settings.MONGODB_URI)
        db_instance.db = db_instance.client.get_default_database()
        
        # Ping to verify connection is actually working
        await db_instance.client.admin.command('ping')
        logger.info("✓ Successfully connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def disconnect_db():
    """Disconnect from MongoDB"""
    if db_instance.client:
        db_instance.client.close()
        logger.info("Disconnected from MongoDB")


async def create_indexes():
    """Create database indexes for better query performance"""
    if db_instance.db is None:
        return
    
    # Doctor collection indexes
    await db_instance.db.doctors.create_index("name")
    await db_instance.db.doctors.create_index("specialization")
    
    # Slot collection indexes
    # Note: Compound index prevents duplicate slots for same doctor/date/time
    await db_instance.db.slots.create_index("doctorId")
    await db_instance.db.slots.create_index("date")
    await db_instance.db.slots.create_index([("doctorId", 1), ("date", 1), ("startTime", 1)], unique=True)
    
    # Token collection indexes
    # These speed up queue queries significantly
    await db_instance.db.tokens.create_index("tokenNumber")
    await db_instance.db.tokens.create_index("patientId")  # for patient history
    await db_instance.db.tokens.create_index("slotId")
    await db_instance.db.tokens.create_index([("slotId", 1), ("queuePosition", 1)])
    await db_instance.db.tokens.create_index([("slotId", 1), ("status", 1)])
    
    logger.info("✓ Database indexes created successfully")


def get_database():
    """Get database instance"""
    return db_instance.db
