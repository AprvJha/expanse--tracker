
import asyncio
from datetime import datetime, timedelta
import random
from app.core.database import db
from bson import ObjectId

async def seed():
    user = await db["users"].find_one({"email": "testuser_e2e@example.com"})
    if not user:
        print("User not found. Please register first.")
        return

    user_id = str(user["_id"])
    
    await db["expenses"].delete_many({"user_id": user_id})
    
    merchants = ["Amazon", "Uber", "Swiggy", "Zomato", "Starbucks", "Netflix", "Airtel", "DMart", "Petrol Pump"]
    categories = ["Shopping", "Transport", "Food", "Food", "Food", "Entertainment", "Utilities", "Shopping", "Transport"]
    
    documents = []
    base_date = datetime.now()
    
    for i in range(1200):
        idx = random.randint(0, len(merchants)-1)
        amount = random.randint(100, 2000)
        is_anomaly = False
        if i % 100 == 0:
            amount = random.randint(20000, 50000)
            is_anomaly = True
            
        documents.append({
            "user_id": user_id,
            "merchant": merchants[idx],
            "amount": float(amount),
            "category": categories[idx],
            "date": base_date - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23)),
            "description": f"{merchants[idx]} transaction {i}",
            "payment_method": "Credit Card",
            "is_anomaly": is_anomaly,
            "source": "seed",
            "created_at": datetime.now()
        })
        
        if len(documents) >= 500:
            await db["expenses"].insert_many(documents)
            documents = []
            
    if documents:
        await db["expenses"].insert_many(documents)
        
    print(f"Successfully seeded 1,200 transactions for {user_id}")

if __name__ == "__main__":
    asyncio.run(seed())
