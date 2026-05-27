# backend/ml/anomaly/zscore_detector.py
import numpy as np
import pandas as pd


def compute_category_stats(df: pd.DataFrame) -> dict:
    """
    Compute mean and std per category.
    This is the baseline each transaction is compared against.
    """
    stats = {}
    for category, group in df.groupby("category"):
        amounts = group["amount"].values
        stats[category] = {
            "mean": float(np.mean(amounts)),
            "std": float(np.std(amounts)),
            "count": int(len(amounts)),
        }
    return stats


def zscore_detect(df: pd.DataFrame, threshold: float = 2.5) -> pd.DataFrame:
    """
    Flag transactions where amount is > threshold std deviations
    above the category mean.

    threshold=2.5 means: flag if amount > mean + 2.5 * std
    Lower threshold = more sensitive (more alerts)
    Higher threshold = less sensitive (fewer alerts)
    """
    stats = compute_category_stats(df)
    df = df.copy()

    df["zscore"] = 0.0
    df["zscore_anomaly"] = False
    df["zscore_deviation"] = ""

    for idx, row in df.iterrows():
        category = row["category"]
        amount = row["amount"]

        if category not in stats:
            continue

        cat_stats = stats[category]

        # Need at least 5 transactions to compute meaningful stats
        if cat_stats["count"] < 5:
            continue

        std = cat_stats["std"]
        mean = cat_stats["mean"]

        if std == 0:
            continue

        z = (amount - mean) / std
        df.at[idx, "zscore"] = round(z, 3)

        if z > threshold:
            df.at[idx, "zscore_anomaly"] = True
            df.at[idx, "zscore_deviation"] = (
                f"{z:.1f}σ above {category} average "
                f"(avg: ₹{mean:,.0f}, this: ₹{amount:,.0f})"
            )

    return df


def evaluate_zscore(df: pd.DataFrame, threshold: float = 3.0) -> dict:
    """
    Evaluate Z-score detector against labeled anomalies.
    Returns precision, recall, f1.
    """
    result_df = zscore_detect(df, threshold)

    true_positives = len(result_df[
        result_df["is_anomaly"] & result_df["zscore_anomaly"]
    ])
    false_positives = len(result_df[
        ~result_df["is_anomaly"] & result_df["zscore_anomaly"]
    ])
    false_negatives = len(result_df[
        result_df["is_anomaly"] & ~result_df["zscore_anomaly"]
    ])

    precision = true_positives / max(true_positives + false_positives, 1)
    recall = true_positives / max(true_positives + false_negatives, 1)
    f1 = 2 * precision * recall / max(precision + recall, 0.001)

    return {
        "method": "zscore",
        "threshold": threshold,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "total_flagged": int(result_df["zscore_anomaly"].sum()),
    }