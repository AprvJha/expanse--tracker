# backend/tests/test_data_cleaner.py
import pytest
import pandas as pd
from app.services.data_cleaner import clean_data


def make_df(rows):
    return pd.DataFrame(rows)


def test_clean_removes_null_amounts():
    """Rows with null amount are dropped."""
    df = make_df([
        {"date": "2026-01-01", "merchant": "Swiggy", "amount": 300},
        {"date": "2026-01-02", "merchant": "Uber", "amount": None},
    ])
    cleaned, stats = clean_data(df)
    assert stats["dropped_nulls"] == 1
    assert len(cleaned) == 1


def test_clean_removes_zero_amounts():
    """Rows with amount=0 are dropped."""
    df = make_df([
        {"date": "2026-01-01", "merchant": "Swiggy", "amount": 0},
        {"date": "2026-01-02", "merchant": "Uber", "amount": 200},
    ])
    cleaned, stats = clean_data(df)
    assert stats["dropped_zero_amounts"] == 1
    assert len(cleaned) == 1


def test_clean_removes_duplicates():
    """Exact duplicate rows (same date+merchant+amount) are dropped."""
    df = make_df([
        {"date": "2026-01-01", "merchant": "Swiggy", "amount": 300},
        {"date": "2026-01-01", "merchant": "Swiggy", "amount": 300},
        {"date": "2026-01-02", "merchant": "Uber", "amount": 200},
    ])
    cleaned, stats = clean_data(df)
    assert stats["dropped_duplicates"] == 1
    assert len(cleaned) == 2


def test_clean_normalizes_merchant_names():
    """Merchant names are stripped and title-cased."""
    df = make_df([
        {"date": "2026-01-01", "merchant": "  swiggy  ", "amount": 300},
        {"date": "2026-01-02", "merchant": "UBER", "amount": 200},
    ])
    cleaned, _ = clean_data(df)
    assert cleaned.iloc[0]["merchant"] == "Swiggy"
    assert cleaned.iloc[1]["merchant"] == "Uber"


def test_clean_rounds_amounts():
    """Amounts are rounded to 2 decimal places."""
    df = make_df([
        {"date": "2026-01-01", "merchant": "Swiggy", "amount": 342.5678},
    ])
    cleaned, _ = clean_data(df)
    assert cleaned.iloc[0]["amount"] == 342.57


def test_clean_stats_sum_correctly():
    """final_rows + all dropped counts = original_rows."""
    df = make_df([
        {"date": "2026-01-01", "merchant": "Swiggy", "amount": 300},
        {"date": "2026-01-01", "merchant": "Swiggy", "amount": 300},
        {"date": "2026-01-02", "merchant": None, "amount": 200},
        {"date": "2026-01-03", "merchant": "Uber", "amount": 0},
        {"date": "2026-01-04", "merchant": "Amazon", "amount": 1500},
    ])
    cleaned, stats = clean_data(df)
    total_dropped = (
        stats["dropped_nulls"] +
        stats["dropped_zero_amounts"] +
        stats["dropped_duplicates"] +
        stats["dropped_bad_dates"]
    )
    assert stats["final_rows"] + total_dropped == stats["original_rows"]