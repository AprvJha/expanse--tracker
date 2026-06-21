import asyncio
import os
import sys
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = os.getenv("MONGODB_URL")
NEW_USER_ID = "6a008f4e5103a259e00d84d3"

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["expense_db"]

    result = await db["expenses"].update_many(
        {"user_id": "69fc6462acc4b24f3c15fbb6"},
        {"$set": {"user_id": NEW_USER_ID}}
    )
    print(f"Reassigned {result.modified_count} transactions to mltest@test.com")

    result2 = await db["expenses"].update_many(
        {"user_id": "690c9cd71d7260496c4b7222"},
        {"$set": {"user_id": NEW_USER_ID}}
    )
    print(f"Reassigned {result2.modified_count} additional transactions")

    result3 = await db["expenses"].update_many(
        {"user_id": "69fc5ba7507b35701dbe8562"},
        {"$set": {"user_id": NEW_USER_ID}}
    )
    print(f"Reassigned {result3.modified_count} additional transactions")

    count = await db["expenses"].count_documents({"user_id": NEW_USER_ID})
    print(f"Total transactions for mltest@test.com: {count}")

    client.close()

if __name__ == "__main__":
    asyncio.run(main())
