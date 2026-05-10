# backend/app/services/csv_parser.py
import pandas as pd
from io import StringIO
from app.services.data_cleaner import clean_data


# Column name mappings for different bank formats
COLUMN_MAPS = {
    "hdfc": {
        "Date": "date",
        "Narration": "merchant",
        "Withdrawal Amt.": "amount",
    },
    "sbi": {
        "Txn Date": "date",
        "Description": "merchant",
        "Debit": "amount",
    },
    "paytm": {
        "date": "date",
        "remarks": "merchant",
        "amount": "amount",
    },
    "icici": {
        "Transaction Date": "date",
        "Transaction Remarks": "merchant",
        "Withdrawal Amount (INR )": "amount",
    },
    "generic": {
        "date": "date",
        "merchant": "merchant",
        "amount": "amount",
    },
}


def detect_format(df: pd.DataFrame) -> str:
    """Detect bank format from column headers."""
    cols = set(df.columns)

    if "Narration" in cols and "Withdrawal Amt." in cols:
        return "hdfc"
    if "Txn Date" in cols and "Debit" in cols:
        return "sbi"
    if "remarks" in cols:
        return "paytm"
    if "Transaction Remarks" in cols:
        return "icici"
    return "generic"


def parse_csv(content: str) -> tuple[list[dict], dict]:
    """
    Main entry point.
    Takes raw CSV string, returns:
    - list of cleaned transaction dicts
    - stats dict for UI feedback
    """
    try:
        df = pd.read_csv(StringIO(content))
    except Exception as e:
        raise ValueError(f"Could not read CSV: {str(e)}")

    # Detect format + rename columns
    fmt = detect_format(df)
    column_map = COLUMN_MAPS[fmt]

    # Only keep columns we care about
    available_cols = {k: v for k, v in column_map.items() if k in df.columns}
    if len(available_cols) < 2:
        raise ValueError(
            f"CSV format not recognized. "
            f"Expected columns like: {list(column_map.keys())}. "
            f"Got: {list(df.columns)}"
        )

    df = df.rename(columns=available_cols)

    # Keep only our 3 core columns
    core_cols = [c for c in ["date", "merchant", "amount"] if c in df.columns]
    df = df[core_cols]

    # Clean the data
    df, stats = clean_data(df)
    stats["format_detected"] = fmt

    # Convert to list of dicts
    records = df.to_dict("records")
    return records, stats