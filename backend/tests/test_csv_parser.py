# backend/tests/test_csv_parser.py
import pytest
from app.services.csv_parser import parse_csv, detect_format
import pandas as pd
from io import StringIO


def test_parse_clean_csv(clean_csv_content):
    """Clean CSV parses with all rows preserved."""
    records, stats = parse_csv(clean_csv_content)
    assert len(records) == 5
    assert stats["dropped_nulls"] == 0
    assert stats["dropped_duplicates"] == 0
    assert stats["format_detected"] == "generic"


def test_parse_removes_duplicates(messy_csv_content):
    """Duplicate rows (same date+merchant+amount) are removed."""
    records, stats = parse_csv(messy_csv_content)
    assert stats["dropped_duplicates"] >= 1


def test_parse_removes_null_merchants(messy_csv_content):
    """Rows with empty merchant are dropped."""
    records, stats = parse_csv(messy_csv_content)
    assert stats["dropped_nulls"] >= 1
    assert all(r["merchant"] for r in records)


def test_parse_removes_zero_amounts(messy_csv_content):
    """Rows with 0 or null amount are dropped."""
    records, stats = parse_csv(messy_csv_content)
    assert all(float(r["amount"]) > 0 for r in records)


def test_detect_generic_format():
    """Generic format detected from standard column names."""
    content = "date,merchant,amount\n2026-01-01,Swiggy,300"
    df = pd.read_csv(StringIO(content))
    fmt = detect_format(df)
    assert fmt == "generic"


def test_detect_hdfc_format():
    """HDFC format detected from Narration column."""
    content = "Date,Narration,Withdrawal Amt.\n01/01/26,SWIGGY*ORDER,300"
    df = pd.read_csv(StringIO(content))
    fmt = detect_format(df)
    assert fmt == "hdfc"


def test_parse_returns_stat_keys(clean_csv_content):
    """Stats dict always contains expected keys."""
    _, stats = parse_csv(clean_csv_content)
    required_keys = [
        "original_rows", "final_rows", "dropped_nulls",
        "dropped_duplicates", "dropped_bad_dates",
        "dropped_zero_amounts", "format_detected"
    ]
    for key in required_keys:
        assert key in stats, f"Missing stat key: {key}"


def test_final_rows_less_than_original(messy_csv_content):
    """After cleaning, final rows must be <= original rows."""
    records, stats = parse_csv(messy_csv_content)
    assert stats["final_rows"] <= stats["original_rows"]