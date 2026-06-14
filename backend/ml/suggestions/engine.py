# backend/ml/suggestions/engine.py
from ml.insights.patterns import (
    to_dataframe,
    category_concentration,
    recurring_expenses,
    monthly_trend,
)
from ml.anomaly.detector import detect_anomalies
from ml.suggestions.rules import (
    check_category_thresholds,
    savings_opportunities,
    subscription_audit,
    diversification_check,
    anomaly_followups,
    forecast_alert,
)

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}


def generate_suggestions(expenses: list[dict]) -> list[dict]:
    """
    Orchestrates Phase 3, 4, 5 outputs into a unified list
    of actionable, rule-based suggestions.
    """
    df = to_dataframe(expenses)
    if df.empty:
        return []

    suggestions = []

    # ── Category concentration (Phase 3) ──────────────
    concentration = category_concentration(df)
    if concentration:
        category_totals = concentration.get("category_totals", {})
        total = sum(category_totals.values())
        months_count = max(df["month_year"].nunique(), 1)

        suggestions += check_category_thresholds(category_totals, total)
        suggestions += savings_opportunities(category_totals, total, months=months_count)

        diversification = diversification_check(concentration)
        if diversification:
            suggestions.append(diversification)

    # ── Recurring expenses (Phase 3) ──────────────────
    recurring = recurring_expenses(df)
    sub_audit = subscription_audit(recurring)
    if sub_audit:
        suggestions.append(sub_audit)

    # ── Anomalies (Phase 4) ────────────────────────────
    try:
        alerts = detect_anomalies(expenses)
        suggestions += anomaly_followups(alerts)
    except Exception:
        pass  # detector not ready — skip gracefully

    # ── Forecast (Phase 5) ──────────────────────────────
    try:
        from ml.prediction.predictor import predict_next_days
        forecast = predict_next_days(expenses, days=30)
        trend = monthly_trend(df)
        fc_alert = forecast_alert(forecast, trend)
        if fc_alert:
            suggestions.append(fc_alert)
    except Exception:
        pass  # predictor not trained yet — skip gracefully

    suggestions.sort(key=lambda s: SEVERITY_ORDER.get(s["severity"], 99))
    return suggestions