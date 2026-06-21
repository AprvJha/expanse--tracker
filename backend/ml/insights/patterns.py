import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def to_dataframe(expenses: list[dict]) -> pd.DataFrame:
    """Convert MongoDB expense list to pandas DataFrame."""
    df = pd.DataFrame(expenses)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].astype(float)
    df["weekday"] = df["date"].dt.dayofweek      # 0=Mon, 6=Sun
    df["is_weekend"] = df["weekday"] >= 5
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    df["day"] = df["date"].dt.day
    df["month_year"] = df["date"].dt.to_period("M")
    return df


def weekend_vs_weekday(df: pd.DataFrame) -> dict:
    """
    Calculate weekend vs weekday spending ratio.
    Returns ratio and daily averages.
    """
    if df.empty:
        return None

    weekend = df[df["is_weekend"]]
    weekday = df[~df["is_weekend"]]

    weekend_days = max(weekend["date"].dt.date.nunique(), 1)
    weekday_days = max(weekday["date"].dt.date.nunique(), 1)

    weekend_daily_avg = weekend["amount"].sum() / weekend_days
    weekday_daily_avg = weekday["amount"].sum() / weekday_days

    ratio = weekend_daily_avg / max(weekday_daily_avg, 1)

    return {
        "weekend_daily_avg": round(weekend_daily_avg, 2),
        "weekday_daily_avg": round(weekday_daily_avg, 2),
        "ratio": round(ratio, 2),
        "weekend_total": round(weekend["amount"].sum(), 2),
        "weekday_total": round(weekday["amount"].sum(), 2),
    }


def category_concentration(df: pd.DataFrame) -> dict:
    """
    Calculate what % of spending top N categories represent.
    """
    if df.empty:
        return None

    total = df["amount"].sum()
    by_category = (
        df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    top3_total = by_category.head(3).sum()
    top3_pct = (top3_total / total) * 100

    top1_pct = (by_category.iloc[0] / total) * 100 if len(by_category) > 0 else 0

    return {
        "top3_categories": by_category.head(3).index.tolist(),
        "top3_percentage": round(top3_pct, 1),
        "top1_category": by_category.index[0] if len(by_category) > 0 else None,
        "top1_percentage": round(top1_pct, 1),
        "category_totals": {k: round(v, 2) for k, v in by_category.items()},
    }


def merchant_frequency(df: pd.DataFrame, top_n: int = 5) -> list[dict]:
    """
    Find most visited merchants.
    Compare current month vs previous month.
    """
    if df.empty:
        return []

    now = datetime.now()
    current_month = df[
        (df["date"].dt.month == now.month) &
        (df["date"].dt.year == now.year)
    ]
    prev_month = df[
        (df["date"].dt.month == (now - timedelta(days=30)).month) &
        (df["date"].dt.year == (now - timedelta(days=30)).year)
    ]

    current_counts = current_month["merchant"].value_counts()
    prev_counts = prev_month["merchant"].value_counts()

    results = []
    for merchant, count in current_counts.head(top_n).items():
        prev_count = prev_counts.get(merchant, 0)
        change_pct = ((count - prev_count) / max(prev_count, 1)) * 100

        results.append({
            "merchant": merchant,
            "visits_this_month": int(count),
            "visits_last_month": int(prev_count),
            "change_pct": round(change_pct, 1),
            "total_spent": round(
                current_month[current_month["merchant"] == merchant]["amount"].sum(), 2
            ),
        })

    return results


def monthly_trend(df: pd.DataFrame) -> list[dict]:
    """
    Monthly spending totals for last 6 months.
    Identifies highest and lowest months.
    """
    if df.empty:
        return []

    monthly = (
        df.groupby("month_year")["amount"]
        .agg(["sum", "count"])
        .reset_index()
        .tail(6)
    )
    monthly.columns = ["month_year", "total", "count"]
    monthly["total"] = monthly["total"].round(2)

    result = monthly.to_dict("records")
    for r in result:
        r["month_year"] = str(r["month_year"])

    return result


def recurring_expenses(df: pd.DataFrame) -> list[dict]:
    """
    Detect recurring charges — same merchant, similar amount, monthly pattern.
    """
    if df.empty:
        return []

    recurring = []
    for merchant, group in df.groupby("merchant"):
        months = group["month_year"].nunique()
        if months < 2:
            continue

        std = group["amount"].std()
        mean = group["amount"].mean()
        cv = std / mean if mean > 0 else 1  # coefficient of variation

        if cv < 0.1:  # less than 10% variation = recurring
            recurring.append({
                "merchant": merchant,
                "amount": round(mean, 2),
                "months_detected": int(months),
                "category": group["category"].mode()[0],
                "total_paid": round(group["amount"].sum(), 2),
            })

    recurring.sort(key=lambda x: x["amount"], reverse=True)
    return recurring[:10]


def highest_spend_month(df: pd.DataFrame) -> dict:
    """Find the highest spending month in the dataset."""
    if df.empty:
        return None

    monthly = df.groupby("month_year")["amount"].sum()
    highest = monthly.idxmax()
    lowest = monthly.idxmin()

    return {
        "highest_month": str(highest),
        "highest_amount": round(monthly[highest], 2),
        "lowest_month": str(lowest),
        "lowest_amount": round(monthly[lowest], 2),
        "current_month_rank": int(
            monthly.rank(ascending=False)[monthly.index[-1]]
        ) if len(monthly) > 0 else None,
    }