import asyncio
from app.core.database import db

async def main():
    total_expenses = await db["expenses"].count_documents({})
    print(f"Total expenses in DB: {total_expenses}")
    
    users = db["users"].find({})
    async for user in users:
        uid = str(user["_id"])
        c = await db["expenses"].count_documents({"user_id": uid})
        print(f"User {user['email']} ({uid}) has {c} expenses")
        
    # Find all distinct user_ids in expenses
    pipeline = [{"$group": {"_id": "$user_id", "count": {"$sum": 1}}}]
    cursor = db["expenses"].aggregate(pipeline)
    async for doc in cursor:
        print(f"Expenses have user_id: {doc['_id']} with count {doc['count']}")

asyncio.run(main())
