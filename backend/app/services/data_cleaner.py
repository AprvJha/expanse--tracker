# backend/app/services/data_cleaner.py
import pandas as pd
from datetime import datetime


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Cleans raw parsed DataFrame.
    Returns cleaned df + stats dict (for showing in upload UI).
    """
    stats = {
        "original_rows": len(df),
        "dropped_nulls": 0,
        "dropped_zero_amounts": 0,
        "dropped_duplicates": 0,
        "dropped_bad_dates": 0,
        "final_rows": 0,
    }

    # 1. Drop rows where amount or merchant is null
    before = len(df)
    df = df.dropna(subset=["amount", "merchant"])
    stats["dropped_nulls"] = before - len(df)

    # 2. Drop zero or negative amounts
    before = len(df)
    df = df[df["amount"] > 0]
    stats["dropped_zero_amounts"] = before - len(df)

    # 3. Parse dates flexibly
    before = len(df)
    df["date"] = pd.to_datetime(df["date"], format="mixed", errors="coerce")
    df = df.dropna(subset=["date"])  # drop rows where date couldn't be parsed
    stats["dropped_bad_dates"] = before - len(df)

    # 4. Clean merchant names
    df["merchant"] = (
        df["merchant"]
        .astype(str)
        .str.strip()
        .str.title()
        .str.replace(r"\s+", " ", regex=True)  # remove double spaces
    )

    # 5. Round amounts to 2 decimal places
    df["amount"] = df["amount"].round(2)

    # 6. Drop exact duplicates (same date + merchant + amount)
    before = len(df)
    df = df.drop_duplicates(subset=["date", "merchant", "amount"])
    stats["dropped_duplicates"] = before - len(df)

    # 7. Reset index
    df = df.reset_index(drop=True)

    stats["final_rows"] = len(df)
    return df, stats