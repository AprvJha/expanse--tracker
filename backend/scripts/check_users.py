import asyncio
import os
import sys
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = os.getenv("MONGODB_URL")

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["expense_db"]

    print("=== Users ===")
    users = await db["users"].find({}, {"email": 1, "name": 1}).to_list(100)
    for u in users:
        print(f"  ID: {u['_id']}  Email: {u.get('email')}  Name: {u.get('name')}")

    print("\n=== Expense groups by user_id ===")
    pipeline = [{"$group": {"_id": "$user_id", "count": {"$sum": 1}}}]
    groups = await db["expenses"].aggregate(pipeline).to_list(100)
    for g in groups:
        print(f"  user_id: {g['_id']}  count: {g['count']}")

    client.close()

if __name__ == "__main__":
    asyncio.run(main())
