# backend/ml/prediction/features.py
import pandas as pd
import numpy as np
from ml.insights.patterns import to_dataframe


def build_daily_features(expenses: list[dict]) -> pd.DataFrame:
    """
    Aggregate expenses by day and build features for prediction.
    Each row = one day with total spend + features.
    """
    df = to_dataframe(expenses)
    if df.empty:
        return pd.DataFrame()

    # Daily totals
    daily = (
        df.groupby(df["date"].dt.date)["amount"]
        .sum()
        .reset_index()
    )
    daily.columns = ["date", "total"]
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date").reset_index(drop=True)

    # Fill missing days with 0
    full_range = pd.date_range(
        start=daily["date"].min(),
        end=daily["date"].max(),
        freq="D"
    )
    daily = daily.set_index("date").reindex(full_range, fill_value=0)
    daily.index.name = "date"
    daily = daily.reset_index()

    # ── Feature Engineering ───────────────────────────
    # Day of week (0=Mon, 6=Sun)
    daily["day_of_week"] = daily["date"].dt.dayofweek

    # Weekend flag
    daily["is_weekend"] = (daily["day_of_week"] >= 5).astype(int)

    # Day of month
    daily["day_of_month"] = daily["date"].dt.day

    # Month
    daily["month"] = daily["date"].dt.month

    # Is payday (1st-3rd of month)
    daily["is_payday"] = (daily["day_of_month"] <= 3).astype(int)

    # Is month end (28th+)
    daily["is_month_end"] = (daily["day_of_month"] >= 28).astype(int)

    # Rolling averages (past spend trends)
    daily["rolling_7d"] = (
        daily["total"].shift(1).rolling(7, min_periods=1).mean()
    )
    daily["rolling_30d"] = (
        daily["total"].shift(1).rolling(30, min_periods=1).mean()
    )

    # Lag features (yesterday, last week same day)
    daily["lag_1"] = daily["total"].shift(1).fillna(0)
    daily["lag_7"] = daily["total"].shift(7).fillna(0)

    return daily


def build_monthly_features(expenses: list[dict]) -> pd.DataFrame:
    """
    Aggregate expenses by month for monthly prediction.
    """
    df = to_dataframe(expenses)
    if df.empty:
        return pd.DataFrame()

    monthly = (
        df.groupby(df["date"].dt.to_period("M"))["amount"]
        .sum()
        .reset_index()
    )
    monthly.columns = ["month", "total"]
    monthly["month_num"] = range(len(monthly))

    # Lag features
    monthly["lag_1"] = monthly["total"].shift(1).fillna(0)
    monthly["lag_2"] = monthly["total"].shift(2).fillna(0)
    monthly["rolling_3m"] = (
        monthly["total"].shift(1).rolling(3, min_periods=1).mean()
    )

    return monthly