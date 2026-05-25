import asyncio
from app.core.database import db
from jose import jwt
from datetime import datetime, timedelta

async def main():
    user = await db["users"].find_one({"email": "insightstest@test.com"})
    if user:
        payload = {
            'sub': str(user["_id"]),
            'email': user["email"],
            'name': user["name"],
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        token = jwt.encode(payload, '23d3b016d7da1097befcb6fb94c438ed8c133ec92bbae0a4516e761b5979cad3', algorithm='HS256')
        print("TOKEN:", token)
    else:
        print("User not found")

asyncio.run(main())
