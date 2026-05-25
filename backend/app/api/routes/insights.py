# backend/app/api/routes/insights.py
from fastapi import APIRouter, Depends
from app.api.routes.auth import get_current_user
from app.core.database import get_database
from ml.insights.behavioral import generate_insights, get_full_analysis

router = APIRouter(prefix="/insights", tags=["insights"])


async def fetch_user_expenses(user_id: str) -> list[dict]:
    """Fetch all expenses for a user from MongoDB."""
    db = get_database()
    cursor = db["expenses"].find(
        {"user_id": user_id},
        {"_id": 0, "merchant": 1, "amount": 1, "category": 1,
         "date": 1, "is_anomaly": 1}
    )
    return await cursor.to_list(length=10000)


@router.get("/")
async def get_insights(current_user: dict = Depends(get_current_user)):
    """
    Get behavioral insight cards for current user.
    Returns list of insight cards with message + severity + data.
    """
    expenses = await fetch_user_expenses(current_user["id"])
    insights = generate_insights(expenses)
    return {
        "count": len(insights),
        "insights": insights,
    }


@router.get("/full")
async def get_full_insights(current_user: dict = Depends(get_current_user)):
    """
    Full analysis — insight cards + all raw pattern data.
    Used by dashboard analytics page.
    """
    expenses = await fetch_user_expenses(current_user["id"])
    return get_full_analysis(expenses)


@router.get("/patterns/weekend")
async def weekend_pattern(current_user: dict = Depends(get_current_user)):
    """Weekend vs weekday spending breakdown."""
    from ml.insights.patterns import to_dataframe, weekend_vs_weekday
    expenses = await fetch_user_expenses(current_user["id"])
    df = to_dataframe(expenses)
    return weekend_vs_weekday(df)


@router.get("/patterns/recurring")
async def recurring_pattern(current_user: dict = Depends(get_current_user)):
    """Detect recurring monthly charges."""
    from ml.insights.patterns import to_dataframe, recurring_expenses
    expenses = await fetch_user_expenses(current_user["id"])
    df = to_dataframe(expenses)
    return {"recurring": recurring_expenses(df)}


@router.get("/patterns/merchants")
async def merchant_pattern(current_user: dict = Depends(get_current_user)):
    """Top merchant frequency + month over month change."""
    from ml.insights.patterns import to_dataframe, merchant_frequency
    expenses = await fetch_user_expenses(current_user["id"])
    df = to_dataframe(expenses)
    return {"merchants": merchant_frequency(df)}