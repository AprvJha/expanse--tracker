# backend/ml/anomaly/detector.py
import pandas as pd
import numpy as np
import asyncio
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
)))
sys.path.append(BASE_DIR)

from ml.anomaly.zscore_detector import zscore_detect, evaluate_zscore
from ml.anomaly.isolation_forest import (
    train_isolation_forest,
    isolation_forest_detect,
    evaluate_isolation_forest,
)
from ml.insights.patterns import to_dataframe


def detect_anomalies(expenses: list[dict]) -> list[dict]:
    """
    Main anomaly detection pipeline.
    Runs both Z-score and Isolation Forest.
    Returns flagged transactions with alert messages.
    """
    df = to_dataframe(expenses)
    if df.empty:
        return []

    # Add is_anomaly column if missing
    if "is_anomaly" not in df.columns:
        df["is_anomaly"] = False

    # Run both detectors
    df = zscore_detect(df, threshold=2.5)
    df = isolation_forest_detect(df)

    # Flag if EITHER detector flags it
    df["detected"] = df["zscore_anomaly"] | df["if_anomaly"]

    # Build alert list
    alerts = []
    flagged = df[df["detected"]].copy()

    for _, row in flagged.iterrows():
        # Determine severity
        if row.get("zscore", 0) > 3.5 or row.get("anomaly_score", 0) > 0.6:
            severity = "high"
        elif row.get("zscore", 0) > 2.5 or row.get("anomaly_score", 0) > 0.4:
            severity = "medium"
        else:
            severity = "low"

        # Detection method
        methods = []
        if row.get("zscore_anomaly"):
            methods.append("z-score")
        if row.get("if_anomaly"):
            methods.append("isolation-forest")

        alerts.append({
            "merchant": row["merchant"],
            "amount": row["amount"],
            "category": row["category"],
            "date": str(row["date"]),
            "severity": severity,
            "zscore": row.get("zscore", 0),
            "anomaly_score": row.get("anomaly_score", 0),
            "detection_methods": methods,
            "message": (
                row.get("zscore_deviation") or
                f"Unusual {row['category']} transaction: ₹{row['amount']:,.0f}"
            ),
            "is_labeled_anomaly": bool(row.get("is_anomaly", False)),
        })

    # Sort by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    alerts.sort(key=lambda x: severity_order[x["severity"]])

    return alerts


def get_anomaly_metrics(expenses: list[dict]) -> dict:
    """
    Evaluate both detectors against labeled anomalies.
    Returns precision/recall/f1 for each method.
    """
    df = to_dataframe(expenses)
    if df.empty or "is_anomaly" not in df.columns:
        return {}

    zscore_metrics = evaluate_zscore(df)
    if_metrics = evaluate_isolation_forest(df)

    labeled_count = int(df["is_anomaly"].sum())

    return {
        "labeled_anomalies": labeled_count,
        "zscore": zscore_metrics,
        "isolation_forest": if_metrics,
        "summary": {
            "best_precision": max(
                zscore_metrics["precision"],
                if_metrics["precision"]
            ),
            "best_recall": max(
                zscore_metrics["recall"],
                if_metrics["recall"]
            ),
        }
    }