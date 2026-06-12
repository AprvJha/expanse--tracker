# backend/ml/prediction/evaluator.py
import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "predictor.pkl")


def get_prediction_metrics() -> dict:
    """
    Return stored model metrics.
    Linear Regression vs Rolling Average baseline comparison.
    THIS is what you show in interviews.
    """
    if not os.path.exists(MODEL_PATH):
        return {"status": "no model trained"}

    data = joblib.load(MODEL_PATH)

    return {
        "status": "loaded",
        "comparison": {
            "linear_regression": {
                "mae": round(data["mae"], 2),
                "mae_pct": round(data["mae_pct"], 2),
            },
            "rolling_average_baseline": {
                "mae": round(data["baseline_mae"], 2),
                "mae_pct": round(data["baseline_mae_pct"], 2),
            },
        },
        "winner": (
            "linear_regression"
            if data["mae"] < data["baseline_mae"]
            else "rolling_average"
        ),
    }