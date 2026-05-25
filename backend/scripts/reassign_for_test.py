import asyncio
import os
import sys
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = os.getenv("MONGODB_URL")
OLD_USER_ID = "6a008f4e5103a259e00d84d3"
NEW_USER_ID = "6a144a1c43a8e8ef270df35a"

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["expense_db"]
    result = await db["expenses"].update_many(
        {"user_id": OLD_USER_ID},
        {"$set": {"user_id": NEW_USER_ID}}
    )
    print(f"Updated {result.modified_count} expenses")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
