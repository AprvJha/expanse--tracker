from fastapi import APIRouter, Depends
from app.api.routes.auth import get_current_user
from app.core.database import get_database
from ml.suggestions.engine import generate_suggestions

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


async def fetch_expenses(user_id: str) -> list[dict]:
    db = get_database()
    cursor = db["expenses"].find(
        {"user_id": user_id},
        {"_id": 0, "merchant": 1, "amount": 1, "category": 1,
         "date": 1, "is_anomaly": 1}
    )
    return await cursor.to_list(length=10000)


@router.get("/")
async def get_suggestions(current_user: dict = Depends(get_current_user)):
    """
    Data-driven suggestions based on spending patterns,
    anomalies, and forecasts. Rule-based — no black box.
    """
    expenses = await fetch_expenses(current_user["id"])
    suggestions = generate_suggestions(expenses)

    return {
        "count": len(suggestions),
        "high_priority": len([s for s in suggestions if s["severity"] == "high"]),
        "medium_priority": len([s for s in suggestions if s["severity"] == "medium"]),
        "info": len([s for s in suggestions if s["severity"] == "info"]),
        "suggestions": suggestions,
    }