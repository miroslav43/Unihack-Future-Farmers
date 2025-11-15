"""MongoDB database configuration and connection management"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from .settings import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MongoDB connection lifecycle"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """Establish database connection"""
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGO_API_KEY,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            await self.client.admin.command('ping')
            
            self.db = self.client[settings.DATABASE_NAME]
            
            # Create indexes
            await self._create_indexes()
            
            logger.info(f"Connected to MongoDB database: {settings.DATABASE_NAME}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        if self.db is None:
            return
        
        # Farmers collection indexes
        await self.db.farmers.create_index("cnp", unique=True)
        await self.db.farmers.create_index("email")
        await self.db.farmers.create_index("created_at")
        
        # Documents collection indexes
        await self.db.documents.create_index("farmer_id")
        await self.db.documents.create_index("document_type")
        await self.db.documents.create_index("status")
        
        # Assessments collection indexes
        await self.db.assessments.create_index("farmer_id")
        await self.db.assessments.create_index("created_at")
        
        # Applications collection indexes
        await self.db.applications.create_index("farmer_id")
        await self.db.applications.create_index("application_type")
        await self.db.applications.create_index("status")
        
        logger.info("Database indexes created successfully")
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return self.db


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncIOMotorDatabase:
    """Dependency for getting database instance in route handlers"""
    return db_manager.get_database()
