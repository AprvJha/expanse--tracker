# backend/app/api/routes/prediction.py
from fastapi import APIRouter, Depends, Query, Response
from app.api.routes.auth import get_current_user
from app.core.database import get_database
from ml.prediction.predictor import train_predictor, predict_next_days
from ml.prediction.evaluator import get_prediction_metrics

router = APIRouter(prefix="/prediction", tags=["prediction"])


async def fetch_expenses(user_id: str) -> list[dict]:
    db = get_database()
    cursor = db["expenses"].find(
        {"user_id": user_id},
        {"_id": 0, "merchant": 1, "amount": 1,
         "category": 1, "date": 1}
    )
    return await cursor.to_list(length=10000)


@router.post("/train")
async def train(current_user: dict = Depends(get_current_user)):
    """
    Train Linear Regression predictor.
    Returns MAE comparison vs rolling average baseline.
    """
    try:
        expenses = await fetch_expenses(current_user["id"])
        metrics = train_predictor(expenses)
        return {"message": "Predictor trained", "metrics": metrics}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@router.get("/forecast")
async def forecast(
    response: Response,
    days: int = Query(default=30, ge=7, le=90),
    current_user: dict = Depends(get_current_user),
):
    """
    Predict spend for next N days (7–90).
    Returns daily predictions + total.
    """
    response.headers["Cache-Control"] = "no-store"
    try:
        expenses = await fetch_expenses(current_user["id"])
        result = predict_next_days(expenses, days=days)
        return result
    except ValueError as e:
        return {"error": str(e)}


@router.get("/metrics")
async def metrics(current_user: dict = Depends(get_current_user)):
    """
    Linear Regression MAE vs Rolling Average MAE.
    The comparison that proves the model adds value.
    """
    return get_prediction_metrics()