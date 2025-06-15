import logging
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.user_activity = None

    async def connect(self):
        """Connect to MongoDB database"""
        try:
            self.client = AsyncIOMotorClient(MONGO_URI)
            self.db = self.client[DB_NAME]
            self.user_activity = self.db.user_activity
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def update_user_activity(self, chat_id, user_id, username=None, first_name=None):
        """Update user's last activity timestamp"""
        try:
            await self.user_activity.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {
                    "$set": {
                        "last_active": datetime.now(),
                        "username": username,
                        "first_name": first_name
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to update user activity: {e}")

    async def get_inactive_users(self, chat_id, since_time):
        """Get users who haven't been active since the specified time"""
        try:
            cursor = self.user_activity.find({
                "chat_id": chat_id,
                "last_active": {"$lt": since_time}
            })
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Failed to get inactive users: {e}")
            return []

    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection")

# Create a global database instance
db = Database()