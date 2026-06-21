import asyncio
import os
import sys
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = os.getenv("MONGODB_URL")

WRONG_USER_ID = "6a144a1c43a8e8ef270df35a"
CORRECT_USER_ID = "69fc6462acc4b24f3c15fbb6"

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["expense_db"]

    before = await db["expenses"].count_documents({"user_id": WRONG_USER_ID})
    print(f"Found {before} transactions under wrong user ID")

    result = await db["expenses"].update_many(
        {"user_id": WRONG_USER_ID},
        {"$set": {"user_id": CORRECT_USER_ID}}
    )
    print(f"✅ Reassigned {result.modified_count} transactions to correct user")

    after = await db["expenses"].count_documents({"user_id": CORRECT_USER_ID})
    print(f"Total transactions for correct user: {after}")

    client.close()

if __name__ == "__main__":
    asyncio.run(main())