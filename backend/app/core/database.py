# backend/app/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGODB_URL

client = AsyncIOMotorClient(MONGODB_URL)
db = client["expense_db"]

def get_database():
    return db