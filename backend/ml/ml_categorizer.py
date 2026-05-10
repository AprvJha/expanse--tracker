import joblib
import os
from ml.categorizer import keyword_categorize

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "categorizer.pkl")

# Load model once at startup
_model_data = None


def load_model():
    global _model_data
    if os.path.exists(MODEL_PATH):
        _model_data = joblib.load(MODEL_PATH)
        print("[SUCCESS] ML categorizer model loaded")
    else:
        print("[WARNING] No ML model found -- using keyword baseline only")


def ml_categorize(merchant: str) -> dict:
    """
    Categorize using ML model if available.
    Falls back to keyword baseline if model not loaded.
    """
    if _model_data is None:
        category, confidence = keyword_categorize(merchant)
        return {
            "category": category,
            "confidence": confidence,
            "method": "keyword",
        }

    pipeline = _model_data["pipeline"]
    category = pipeline.predict([merchant])[0]
    proba = pipeline.predict_proba([merchant])[0]
    confidence = float(max(proba))

    return {
        "category": category,
        "confidence": round(confidence, 3),
        "method": "ml",
    }


def bulk_ml_categorize(merchants: list[str]) -> list[dict]:
    """Categorize a list of merchants."""
    return [ml_categorize(m) for m in merchants]


def get_model_metrics() -> dict:
    """Return stored model performance metrics."""
    if _model_data is None:
        return {"status": "no model loaded"}

    return {
        "status": "loaded",
        "baseline_accuracy": round(_model_data["baseline_accuracy"], 4),
        "ml_accuracy": round(_model_data["ml_accuracy"], 4),
        "improvement": round(_model_data["improvement"], 4),
        "trained_at": _model_data["trained_at"],
        "train_size": _model_data["train_size"],
        "test_size": _model_data["test_size"],
    }