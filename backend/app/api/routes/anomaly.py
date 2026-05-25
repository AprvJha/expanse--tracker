# backend/app/api/routes/anomaly.py
from fastapi import APIRouter, Depends
from app.api.routes.auth import get_current_user
from app.core.database import get_database
from ml.anomaly.detector import detect_anomalies, get_anomaly_metrics
from ml.anomaly.isolation_forest import train_isolation_forest
from ml.insights.patterns import to_dataframe

router = APIRouter(prefix="/anomaly", tags=["anomaly"])


async def fetch_expenses(user_id: str) -> list[dict]:
    db = get_database()
    cursor = db["expenses"].find(
        {"user_id": user_id},
        {"_id": 0, "merchant": 1, "amount": 1, "category": 1,
         "date": 1, "is_anomaly": 1}
    )
    return await cursor.to_list(length=10000)


@router.get("/detect")
async def detect(current_user: dict = Depends(get_current_user)):
    """
    Run anomaly detection on all user transactions.
    Returns list of flagged transactions with severity + message.
    """
    expenses = await fetch_expenses(current_user["id"])
    alerts = detect_anomalies(expenses)

    return {
        "total_transactions": len(expenses),
        "anomalies_detected": len(alerts),
        "high": len([a for a in alerts if a["severity"] == "high"]),
        "medium": len([a for a in alerts if a["severity"] == "medium"]),
        "low": len([a for a in alerts if a["severity"] == "low"]),
        "alerts": alerts,
    }


@router.get("/metrics")
async def anomaly_metrics(current_user: dict = Depends(get_current_user)):
    """
    Evaluate detection accuracy against labeled anomalies.
    Returns precision/recall/f1 for Z-score and Isolation Forest.
    THIS is what you show in interviews.
    """
    expenses = await fetch_expenses(current_user["id"])
    return get_anomaly_metrics(expenses)


@router.post("/train")
async def train_model(current_user: dict = Depends(get_current_user)):
    """Train/retrain the Isolation Forest model."""
    expenses = await fetch_expenses(current_user["id"])
    df = to_dataframe(expenses)

    if len(df) < 50:
        return {"error": "Need at least 50 transactions to train"}

    train_isolation_forest(df)
    return {"message": "Isolation Forest trained successfully",
            "trained_on": len(df)}