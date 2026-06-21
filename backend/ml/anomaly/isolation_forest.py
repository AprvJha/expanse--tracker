import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "isolation_forest.pkl")


def build_features(df: pd.DataFrame) -> np.ndarray:
    """
    Improved feature matrix.
    Added: amount relative to category mean (normalized amount)
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    le = LabelEncoder()
    df["category_encoded"] = le.fit_transform(df["category"].astype(str))

    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    df["log_amount"] = np.log1p(df["amount"])

    category_means = df.groupby("category")["amount"].transform("mean")
    category_stds = df.groupby("category")["amount"].transform("std").fillna(1)
    df["amount_vs_category"] = (df["amount"] - category_means) / category_stds

    feature_df = df[[
        "log_amount",
        "category_encoded",
        "day_of_week",
        "day_of_month",
        "is_weekend",
        "amount_vs_category",
    ]].fillna(0)
    features = feature_df.values

    return features, le


def train_isolation_forest(df: pd.DataFrame, contamination: float = 0.01):
    """
    Train Isolation Forest model.
    contamination = expected proportion of anomalies (5% = 0.05)
    """
    features, le = build_features(df)

    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(features)

    joblib.dump({"model": model, "encoder": le}, MODEL_PATH)
    print(f"[SUCCESS] Isolation Forest saved to {MODEL_PATH}")

    return model, le


def load_isolation_forest():
    """Load saved model if exists."""
    if os.path.exists(MODEL_PATH):
        data = joblib.load(MODEL_PATH)
        return data["model"], data["encoder"]
    return None, None


def isolation_forest_detect(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect anomalies using Isolation Forest.
    Returns df with if_anomaly and anomaly_score columns.
    """
    model, le = load_isolation_forest()
    df = df.copy()

    if model is None:
        df["if_anomaly"] = False
        df["anomaly_score"] = 0.0
        return df

    df["category_encoded"] = 0
    try:
        df["category_encoded"] = le.transform(df["category"].astype(str))
    except Exception:
        pass

    df["day_of_week"] = pd.to_datetime(df["date"]).dt.dayofweek
    df["day_of_month"] = pd.to_datetime(df["date"]).dt.day
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["log_amount"] = np.log1p(df["amount"])

    category_means = df.groupby("category")["amount"].transform("mean")
    category_stds = df.groupby("category")["amount"].transform("std").fillna(1)
    df["amount_vs_category"] = (df["amount"] - category_means) / category_stds

    feature_df = df[[
        "log_amount",
        "category_encoded",
        "day_of_week",
        "day_of_month",
        "is_weekend",
        "amount_vs_category",
    ]].fillna(0)
    features = feature_df.values

    predictions = model.predict(features)
    scores = model.score_samples(features)

    df["if_anomaly"] = predictions == -1
    df["anomaly_score"] = np.round(-scores, 3)  # higher = more anomalous

    return df


def evaluate_isolation_forest(df: pd.DataFrame) -> dict:
    """Evaluate against labeled anomalies."""
    model, le = load_isolation_forest()
    if model is None:
        return None

    result_df = isolation_forest_detect(df)

    true_positives = len(result_df[
        result_df["is_anomaly"] & result_df["if_anomaly"]
    ])
    false_positives = len(result_df[
        ~result_df["is_anomaly"] & result_df["if_anomaly"]
    ])
    false_negatives = len(result_df[
        result_df["is_anomaly"] & ~result_df["if_anomaly"]
    ])

    precision = true_positives / max(true_positives + false_positives, 1)
    recall = true_positives / max(true_positives + false_negatives, 1)
    f1 = 2 * precision * recall / max(precision + recall, 0.001)

    return {
        "method": "isolation_forest",
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "total_flagged": int(result_df["if_anomaly"].sum()),
    }