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
    Ensure all ML models exist on disk, training them from MongoDB
    data if missing. Runs on every cold start — handles ephemeral
    deployment filesystems where local .pkl files don't persist.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)

    # ── Categorizer (Phase 2) ──────────────────────────
    if not os.path.exists(CATEGORIZER_PATH):
        print("[bootstrap] Training categorizer...")
        from ml.trainer import train
        try:
            await train()
        except Exception as e:
            print(f"[bootstrap] Categorizer training skipped: {e}")
    else:
        print("[bootstrap] Categorizer model found")

    expenses = await fetch_all_expenses()

    # ── Isolation Forest (Phase 4) ─────────────────────
    if not os.path.exists(ISOLATION_FOREST_PATH):
        print("[bootstrap] Training Isolation Forest...")
        if len(expenses) >= 50:
            from ml.insights.patterns import to_dataframe
            from ml.anomaly.isolation_forest import train_isolation_forest
            df = to_dataframe(expenses)
            train_isolation_forest(df)
        else:
            print("[bootstrap] Not enough data for Isolation Forest")
    else:
        print("[bootstrap] Isolation Forest model found")

    # ── Predictor (Phase 5) ────────────────────────────
    if not os.path.exists(PREDICTOR_PATH):
        print("[bootstrap] Training predictor...")
        from ml.prediction.predictor import train_predictor
        try:
            train_predictor(expenses)
        except Exception as e:
            print(f"[bootstrap] Predictor training skipped: {e}")
    else:
        print("[bootstrap] Predictor model found")