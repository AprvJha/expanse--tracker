import asyncio
from dotenv import load_dotenv
load_dotenv()
from app.core.database import get_database

async def main():
    db = get_database()
    cursor = db["expenses"].find({"user_id": "69fc6462acc4b24f3c15fbb6", "is_anomaly": True})
    docs = await cursor.to_list(length=100)
    print(f"Total labeled anomalies: {len(docs)}")
    for d in docs:
        print(f"- {d.get('merchant')}: {d.get('amount')} (source: {d.get('source')}, category: {d.get('category')})")

asyncio.run(main())
