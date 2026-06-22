# backend/tests/test_anomaly.py
import pytest
from ml.anomaly.zscore_detector import zscore_detect, evaluate_zscore
from ml.anomaly.detector import detect_anomalies
from ml.insights.patterns import to_dataframe


def test_zscore_flags_obvious_outlier(expenses_with_anomaly):
    """Z-score must flag an ₹89,000 transaction in ₹500 avg dataset."""
    df = to_dataframe(expenses_with_anomaly)
    result_df = zscore_detect(df, threshold=2.5)
    flagged = result_df[result_df["zscore_anomaly"]]
    assert len(flagged) >= 1
    assert any(row["amount"] == 89000 for _, row in flagged.iterrows())


def test_zscore_no_false_positives_on_uniform_data():
    """Z-score should NOT flag anything in perfectly uniform data."""
    from tests.conftest import make_expense
    uniform = [make_expense("Swiggy", 500, "Food", days_ago=i) for i in range(50)]
    df = to_dataframe(uniform)
    result_df = zscore_detect(df, threshold=3.0)
    assert result_df["zscore_anomaly"].sum() == 0


def test_zscore_severity_high_for_extreme_outlier(expenses_with_anomaly):
    """Extreme outliers must appear as HIGH severity."""
    alerts = detect_anomalies(expenses_with_anomaly)
    high_alerts = [a for a in alerts if a["severity"] == "high"]
    assert len(high_alerts) >= 1


def test_anomaly_alert_structure(expenses_with_anomaly):
    """Every alert has required fields."""
    alerts = detect_anomalies(expenses_with_anomaly)
    required = ["merchant", "amount", "category", "severity",
                "message", "detection_methods", "is_labeled_anomaly"]
    for alert in alerts:
        for field in required:
            assert field in alert, f"Missing field: {field}"


def test_labeled_anomaly_detected(expenses_with_anomaly):
    """The labeled anomaly (is_anomaly=True) must appear in alerts."""
    alerts = detect_anomalies(expenses_with_anomaly)
    labeled_found = any(a["is_labeled_anomaly"] for a in alerts)
    assert labeled_found


def test_zscore_evaluate_returns_metrics(expenses_with_anomaly):
    """Evaluation returns all required metric keys."""
    df = to_dataframe(expenses_with_anomaly)
    metrics = evaluate_zscore(df)
    for key in ["precision", "recall", "f1", "total_flagged",
                "true_positives", "false_positives"]:
        assert key in metrics


def test_empty_expenses_returns_no_alerts():
    """Empty input returns empty alert list."""
    alerts = detect_anomalies([])
    assert alerts == []