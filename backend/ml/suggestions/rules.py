from ml.suggestions.benchmarks import (
    CATEGORY_BENCHMARKS,
    DEFAULT_BENCHMARK,
    SAVINGS_REDUCTION_PCT,
    CONCENTRATION_THRESHOLD,
    ANOMALY_FOLLOWUP_LIMIT,
    FORECAST_INCREASE_THRESHOLD,
)


def check_category_thresholds(category_totals: dict, total: float) -> list[dict]:
    """Flag categories that exceed their benchmark % of total spend."""
    if total <= 0:
        return []

    suggestions = []
    for category, amount in category_totals.items():
        pct = (amount / total) * 100
        benchmark = CATEGORY_BENCHMARKS.get(category, DEFAULT_BENCHMARK)

        if pct > benchmark:
            severity = "high" if pct > benchmark * 1.5 else "medium"
            suggestions.append({
                "type": "category_threshold",
                "severity": severity,
                "title": f"{category} is {pct:.1f}% of your spending",
                "message": (
                    f"{category} accounts for {pct:.1f}% of total expenses — "
                    f"above the typical {benchmark}% guideline"
                ),
                "recommendation": f"Consider setting a monthly {category} budget",
                "data": {
                    "category": category,
                    "current_percentage": round(pct, 1),
                    "benchmark_percentage": benchmark,
                    "category_total": round(amount, 2),
                },
            })

    return suggestions


def savings_opportunities(category_totals: dict, total: float, months: int = 1) -> list[dict]:
    """For categories over benchmark, calculate savings from a reduction."""
    if total <= 0:
        return []

    suggestions = []
    for category, amount in category_totals.items():
        pct = (amount / total) * 100
        benchmark = CATEGORY_BENCHMARKS.get(category, DEFAULT_BENCHMARK)

        if pct > benchmark:
            monthly_avg = amount / max(months, 1)
            monthly_savings = monthly_avg * (SAVINGS_REDUCTION_PCT / 100)
            yearly_savings = monthly_savings * 12

            suggestions.append({
                "type": "savings_opportunity",
                "severity": "info",
                "title": f"Potential savings: ₹{monthly_savings:,.0f}/month",
                "message": (
                    f"Reducing {category} spend by {SAVINGS_REDUCTION_PCT}% "
                    f"would save ₹{monthly_savings:,.0f}/month — "
                    f"₹{yearly_savings:,.0f}/year"
                ),
                "recommendation": f"Try a {SAVINGS_REDUCTION_PCT}% reduction target for {category} next month",
                "data": {
                    "category": category,
                    "current_monthly_avg": round(monthly_avg, 2),
                    "reduction_pct": SAVINGS_REDUCTION_PCT,
                    "monthly_savings": round(monthly_savings, 2),
                    "yearly_savings": round(yearly_savings, 2),
                },
            })

    return suggestions


def subscription_audit(recurring: list[dict]) -> dict | None:
    """Summarize recurring subscription costs."""
    if not recurring:
        return None

    total_monthly = sum(r["amount"] for r in recurring)
    total_yearly = total_monthly * 12

    return {
        "type": "subscription_audit",
        "severity": "info",
        "title": f"₹{total_monthly:,.0f}/month in recurring subscriptions",
        "message": (
            f"You have {len(recurring)} recurring charges totaling "
            f"₹{total_monthly:,.0f}/month (₹{total_yearly:,.0f}/year)"
        ),
        "recommendation": "Review which subscriptions you actively use",
        "data": {
            "subscriptions": [
                {"merchant": r["merchant"], "amount": r["amount"], "category": r["category"]}
                for r in recurring
            ],
            "total_monthly": round(total_monthly, 2),
            "total_yearly": round(total_yearly, 2),
        },
    }


def diversification_check(concentration: dict) -> dict | None:
    """Flag if spending is too concentrated in few categories."""
    if not concentration:
        return None

    top3_pct = concentration.get("top3_percentage", 0)
    if top3_pct <= CONCENTRATION_THRESHOLD:
        return None

    top3 = concentration.get("top3_categories", [])
    severity = "high" if top3_pct > 80 else "medium"

    return {
        "type": "diversification",
        "severity": severity,
        "title": f"Top 3 categories = {top3_pct}% of spending",
        "message": (
            f"{', '.join(top3)} make up {top3_pct}% of your expenses — "
            f"limited spread across categories"
        ),
        "recommendation": (
            "Review 'Uncategorized' transactions for clearer insights"
            if "Uncategorized" in top3
            else "Consider whether this concentration aligns with your priorities"
        ),
        "data": {
            "top3_categories": top3,
            "top3_percentage": top3_pct,
        },
    }


def anomaly_followups(alerts: list[dict], limit: int = ANOMALY_FOLLOWUP_LIMIT) -> list[dict]:
    """Convert high-severity anomalies into suggestions, deduped by merchant+amount+date."""
    suggestions = []
    seen = set()

    for alert in alerts:
        if alert["severity"] != "high":
            continue

        key = (alert["merchant"], alert["amount"], alert["date"])
        if key in seen:
            continue
        seen.add(key)

        suggestions.append({
            "type": "anomaly_followup",
            "severity": "high",
            "title": f"Unusual ₹{alert['amount']:,.0f} {alert['category']} transaction detected",
            "message": alert["message"],
            "recommendation": "Verify this transaction is correct — large outliers can skew your monthly trends",
            "data": {
                "merchant": alert["merchant"],
                "amount": alert["amount"],
                "category": alert["category"],
                "date": alert["date"],
            },
        })

        if len(suggestions) >= limit:
            break

    return suggestions


def forecast_alert(forecast: dict, trend: list[dict]) -> dict | None:
    """Compare predicted total vs the last COMPLETE month's total."""
    if not forecast or not trend:
        return None

    predicted_total = forecast.get("total_predicted", 0)

    if len(trend) >= 2:
        previous_total = trend[-2]["total"]
    else:
        previous_total = trend[-1]["total"]

    if previous_total <= 0:
        return None

    change_pct = ((predicted_total - previous_total) / previous_total) * 100

    if change_pct < FORECAST_INCREASE_THRESHOLD:
        return None

    severity = "high" if change_pct > 25 else "medium"

    return {
        "type": "forecast_alert",
        "severity": severity,
        "title": f"Projected to exceed last month's spend by {change_pct:.1f}%",
        "message": (
            f"Based on current trends, this month's total is forecasted "
            f"at ₹{predicted_total:,.0f} — up from ₹{previous_total:,.0f} last month"
        ),
        "recommendation": "Review your top spending categories before month-end",
        "data": {
            "predicted_total": round(predicted_total, 2),
            "previous_total": round(previous_total, 2),
            "change_pct": round(change_pct, 1),
        },
    }