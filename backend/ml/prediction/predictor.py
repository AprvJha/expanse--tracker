import pandas as pd
import numpy as np
import joblib
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from ml.prediction.features import build_daily_features, build_monthly_features

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "predictor.pkl")

FEATURE_COLS = [
    "day_of_week", "is_weekend", "day_of_month",
    "month", "is_payday", "is_month_end",
    "rolling_7d", "rolling_30d", "lag_1", "lag_7",
]


def train_predictor(expenses: list[dict]) -> dict:
    """
    Train Linear Regression on daily spend data.
    Returns model metrics.
    """
    daily = build_daily_features(expenses)

    if len(daily) < 30:
        raise ValueError("Need at least 30 days of data to train")

    daily = daily.dropna(subset=FEATURE_COLS)

    X = daily[FEATURE_COLS].values
    y = daily["total"].values

    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    y_pred = np.maximum(y_pred, 0)

    mae = float(np.mean(np.abs(y_test - y_pred)))
    rmse = float(np.sqrt(np.mean((y_test - y_pred) ** 2)))
    avg_spend = float(np.mean(y_test))
    mae_pct = (mae / avg_spend * 100) if avg_spend > 0 else 0

    rolling_pred = daily["rolling_7d"].values[split:]
    baseline_mae = float(np.mean(np.abs(y_test - rolling_pred)))
    baseline_mae_pct = (baseline_mae / avg_spend * 100) if avg_spend > 0 else 0

    joblib.dump({
        "model": model,
        "scaler": scaler,
        "mae": mae,
        "rmse": rmse,
        "mae_pct": mae_pct,
        "baseline_mae": baseline_mae,
        "baseline_mae_pct": baseline_mae_pct,
        "avg_daily_spend": avg_spend,
    }, MODEL_PATH)

    print(f"[OK] Predictor saved")
    print(f"   Linear Regression MAE: Rs.{mae:.0f} ({mae_pct:.1f}%)")
    print(f"   Rolling Average MAE:   Rs.{baseline_mae:.0f} ({baseline_mae_pct:.1f}%)")

    return {
        "linear_regression": {
            "mae": round(mae, 2),
            "mae_pct": round(mae_pct, 2)
        },
        "rolling_average_baseline": {
            "mae": round(baseline_mae, 2),
            "mae_pct": round(baseline_mae_pct, 2)
        },
        "avg_daily_spend": round(avg_spend, 2),
        "train_days": split,
        "test_days": len(X) - split
    }


def predict_next_days(expenses: list[dict], days: int = 30) -> dict:
    """
    Predict spend for next N days.
    Returns daily predictions + total.
    """
    if not expenses:
        return {
            "days": days,
            "total_predicted": 0,
            "avg_daily_predicted": 0,
            "predictions": [],
            "message": "No expense data available for predictions.",
        }

    if not os.path.exists(MODEL_PATH):
        raise ValueError("Model not trained yet. Call /prediction/train first.")

    model_data = joblib.load(MODEL_PATH)
    model = model_data["model"]
    scaler = model_data["scaler"]

    daily = build_daily_features(expenses)

    if daily.empty or len(daily) < 7:
        raise ValueError("Need at least 7 days of data to forecast.")

    last_row = daily.iloc[-1]
    rolling_7d = last_row.get("rolling_7d", 0) or 0
    rolling_30d = last_row.get("rolling_30d", 0) or 0
    last_total = last_row.get("total", 0) or 0
    lag_7_total = daily.iloc[-7]["total"] if len(daily) >= 7 else 0

    start_date = pd.Timestamp.now().normalize() + pd.Timedelta(days=1)
    predictions = []

    for i in range(days):
        future_date = start_date + pd.Timedelta(days=i)
        is_weekend = future_date.dayofweek >= 5

        features = np.array([[
            future_date.dayofweek,        # day_of_week
            int(is_weekend),              # is_weekend
            future_date.day,              # day_of_month
            future_date.month,            # month
            int(future_date.day <= 3),    # is_payday
            int(future_date.day >= 28),   # is_month_end
            rolling_7d,                   # rolling_7d
            rolling_30d,                  # rolling_30d
            last_total,                   # lag_1
            lag_7_total,                  # lag_7
        ]])

        features_scaled = scaler.transform(features)
        pred = float(max(model.predict(features_scaled)[0], 0))

        predictions.append({
            "date": future_date.strftime("%Y-%m-%d"),
            "predicted_amount": round(pred, 2),
            "is_weekend": is_weekend,
        })

        lag_7_total = last_total
        last_total = pred
        rolling_7d = (rolling_7d * 6 + pred) / 7
        rolling_30d = (rolling_30d * 29 + pred) / 30

    total = sum(p["predicted_amount"] for p in predictions)
    avg_daily = total / days if days > 0 else 0

    return {
        "days": days,
        "total_predicted": round(total, 2),
        "avg_daily_predicted": round(avg_daily, 2),
        "predictions": predictions,
    }