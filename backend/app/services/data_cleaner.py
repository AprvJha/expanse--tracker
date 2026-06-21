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

    before = len(df)
    df = df.dropna(subset=["amount", "merchant"])
    stats["dropped_nulls"] = before - len(df)

    before = len(df)
    df = df[df["amount"] > 0]
    stats["dropped_zero_amounts"] = before - len(df)

    before = len(df)
    df["date"] = pd.to_datetime(df["date"], format="mixed", errors="coerce")
    df = df.dropna(subset=["date"])
    stats["dropped_bad_dates"] = before - len(df)

    df["merchant"] = (
        df["merchant"]
        .astype(str)
        .str.strip()
        .str.title()
        .str.replace(r"\s+", " ", regex=True)
    )

    df["amount"] = df["amount"].round(2)

    before = len(df)
    df = df.drop_duplicates(subset=["date", "merchant", "amount"])
    stats["dropped_duplicates"] = before - len(df)

    df = df.reset_index(drop=True)

    stats["final_rows"] = len(df)
    return df, stats