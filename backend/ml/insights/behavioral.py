# backend/ml/insights/behavioral.py
from ml.insights.patterns import (
    to_dataframe,
    weekend_vs_weekday,
    category_concentration,
    merchant_frequency,
    monthly_trend,
    recurring_expenses,
    highest_spend_month,
)


def generate_insights(expenses: list[dict]) -> list[dict]:
    """
    Main entry point.
    Takes raw expense list, returns list of insight cards.
    Each card has: type, message, severity, data
    """
    df = to_dataframe(expenses)
    if df.empty:
        return []

    insights = []

    # ── 1. Weekend vs Weekday ─────────────────────────
    ww = weekend_vs_weekday(df)
    if ww and ww["ratio"] > 1.2:
        insights.append({
            "type": "weekend_pattern",
            "severity": "info",
            "message": f"Weekend spending is {ww['ratio']}× your weekday average",
            "sub": f"Weekend daily avg: ₹{ww['weekend_daily_avg']:,.0f} vs Weekday: ₹{ww['weekday_daily_avg']:,.0f}",
            "data": ww,
        })

    # ── 2. Category Concentration ─────────────────────
    cc = category_concentration(df)
    if cc and cc["top3_percentage"] > 60:
        top3 = ", ".join(cc["top3_categories"])
        insights.append({
            "type": "concentration",
            "severity": "warning" if cc["top3_percentage"] > 80 else "info",
            "message": f"Top 3 categories = {cc['top3_percentage']}% of your expenses",
            "sub": f"{top3}",
            "data": cc,
        })

    # ── 3. Dominant Category ──────────────────────────
    if cc and cc["top1_percentage"] > 35:
        insights.append({
            "type": "dominant_category",
            "severity": "warning",
            "message": f"{cc['top1_category']} alone = {cc['top1_percentage']}% of total spending",
            "sub": "Consider reviewing this category",
            "data": {"category": cc["top1_category"], "percentage": cc["top1_percentage"]},
        })

    # ── 4. Merchant Frequency ─────────────────────────
    freq = merchant_frequency(df)
    for merchant_data in freq[:2]:
        if merchant_data["change_pct"] > 30:
            insights.append({
                "type": "merchant_spike",
                "severity": "info",
                "message": f"{merchant_data['merchant']} visits up {merchant_data['change_pct']}% vs last month",
                "sub": f"{merchant_data['visits_this_month']} visits · ₹{merchant_data['total_spent']:,.0f} spent",
                "data": merchant_data,
            })

    # ── 5. Recurring Expenses ─────────────────────────
    recurring = recurring_expenses(df)
    if recurring:
        total_recurring = sum(r["amount"] for r in recurring)
        names = ", ".join(r["merchant"] for r in recurring[:3])
        insights.append({
            "type": "recurring",
            "severity": "info",
            "message": f"₹{total_recurring:,.0f}/month in recurring charges detected",
            "sub": f"{names}{'...' if len(recurring) > 3 else ''}",
            "data": {"recurring": recurring, "total": total_recurring},
        })

    # ── 6. Highest Spend Month ────────────────────────
    monthly = highest_spend_month(df)
    if monthly and monthly["current_month_rank"] == 1:
        insights.append({
            "type": "monthly_high",
            "severity": "warning",
            "message": "This is your highest spending month on record",
            "sub": f"₹{monthly['highest_amount']:,.0f} total",
            "data": monthly,
        })

    # ── 7. Monthly Trend ──────────────────────────────
    trend = monthly_trend(df)
    if len(trend) >= 2:
        last = trend[-1]["total"]
        prev = trend[-2]["total"]
        change = ((last - prev) / max(prev, 1)) * 100
        if abs(change) > 20:
            direction = "up" if change > 0 else "down"
            insights.append({
                "type": "monthly_change",
                "severity": "warning" if change > 20 else "info",
                "message": f"Spending {direction} {abs(change):.1f}% vs last month",
                "sub": f"₹{last:,.0f} this month vs ₹{prev:,.0f} last month",
                "data": {"current": last, "previous": prev, "change_pct": round(change, 1)},
            })

    return insights


def get_full_analysis(expenses: list[dict]) -> dict:
    """
    Returns everything — insights + raw pattern data.
    Used by dashboard for full analytics view.
    """
    df = to_dataframe(expenses)
    if df.empty:
        return {"insights": [], "patterns": {}}

    return {
        "insights": generate_insights(expenses),
        "patterns": {
            "weekend_vs_weekday": weekend_vs_weekday(df),
            "category_concentration": category_concentration(df),
            "merchant_frequency": merchant_frequency(df),
            "monthly_trend": monthly_trend(df),
            "recurring_expenses": recurring_expenses(df),
            "highest_spend_month": highest_spend_month(df),
        }
    }