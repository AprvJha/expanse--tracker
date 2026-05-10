import asyncio
import os
import sys
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = os.getenv("MONGODB_URL")
YOUR_USER_ID = "69fc6462acc4b24f3c15fbb6"

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["expense_db"]

    result = await db["expenses"].update_many(
        {"user_id": "sample_user_001"},
        {"$set": {"user_id": YOUR_USER_ID}}
    )

    print(f"✅ Updated {result.modified_count} transactions")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())