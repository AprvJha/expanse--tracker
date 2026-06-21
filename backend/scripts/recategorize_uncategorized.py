import asyncio, os, sys
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

from motor.motor_asyncio import AsyncIOMotorClient
from ml.ml_categorizer import ml_categorize, load_model

MONGODB_URL = os.getenv("MONGODB_URL")

async def main():
    load_model()
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["expense_db"]
    collection = db["expenses"]

    docs = await collection.find({"category": "Uncategorized"}).to_list(length=1000)
    print(f"Found {len(docs)} uncategorized transactions")

    updated = 0
    for doc in docs:
        result = ml_categorize(doc["merchant"])
        if result["category"] != "Uncategorized":
            await collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"category": result["category"], "confidence": result["confidence"]}}
            )
            updated += 1

    print(f"Recategorized {updated} transactions")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())