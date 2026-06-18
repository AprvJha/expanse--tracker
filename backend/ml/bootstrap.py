# backend/ml/bootstrap.py
import os
from app.core.database import get_database

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")

CATEGORIZER_PATH = os.path.join(MODELS_DIR, "categorizer.pkl")
ISOLATION_FOREST_PATH = os.path.join(MODELS_DIR, "isolation_forest.pkl")
PREDICTOR_PATH = os.path.join(MODELS_DIR, "predictor.pkl")


async def fetch_all_expenses() -> list[dict]:
    db = get_database()
    cursor = db["expenses"].find(
        {},
        {"_id": 0, "merchant": 1, "amount": 1, "category": 1,
         "date": 1, "is_anomaly": 1}
    )
    return await cursor.to_list(length=20000)


async def bootstrap_models():
    """
    Always retrain all models on startup. This guarantees the
    models match the currently-installed library versions and
    avoids cross-version pickle incompatibility if Render's disk
    persists stale files across redeploys.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)

    print("[bootstrap] Training categorizer...")
    from ml.trainer import train
    try:
        await train()
    except Exception as e:
        print(f"[bootstrap] Categorizer training failed: {e}")

    expenses = await fetch_all_expenses()

    print("[bootstrap] Training Isolation Forest...")
    if len(expenses) >= 50:
        from ml.insights.patterns import to_dataframe
        from ml.anomaly.isolation_forest import train_isolation_forest
        df = to_dataframe(expenses)
        train_isolation_forest(df)
    else:
        print("[bootstrap] Not enough data for Isolation Forest")

    print("[bootstrap] Training predictor...")
    from ml.prediction.predictor import train_predictor
    try:
        train_predictor(expenses)
    except Exception as e:
        print(f"[bootstrap] Predictor training failed: {e}")