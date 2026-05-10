# backend/app/services/auth_service.py
from datetime import datetime
from app.core.database import get_database
from app.core.security import hash_password, verify_password, create_access_token

db = get_database()
users_collection = db["users"]


async def register_user(email: str, password: str, name: str) -> dict:
    """
    Register a new user.
    Raises ValueError if email already exists.
    """
    # Check if email already taken
    existing = await users_collection.find_one({"email": email})
    if existing:
        raise ValueError("Email already registered")

    # Create user document
    user = {
        "email": email.lower().strip(),
        "name": name.strip(),
        "password": hash_password(password),
        "created_at": datetime.now(),
    }

    result = await users_collection.insert_one(user)

    return {
        "id": str(result.inserted_id),
        "email": user["email"],
        "name": user["name"],
    }


async def login_user(email: str, password: str) -> dict:
    """
    Authenticate user.
    Raises ValueError if credentials are wrong.
    """
    user = await users_collection.find_one({"email": email.lower().strip()})

    if not user:
        raise ValueError("Invalid email or password")

    if not verify_password(password, user["password"]):
        raise ValueError("Invalid email or password")

    # Create JWT token
    token = create_access_token(data={
        "sub": str(user["_id"]),
        "email": user["email"],
        "name": user["name"],
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
        }
    }


async def get_user_by_id(user_id: str) -> dict | None:
    """Fetch user by ID. Used by JWT middleware."""
    from bson import ObjectId
    try:
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
        }
    except Exception:
        return None