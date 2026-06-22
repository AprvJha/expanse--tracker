# backend/tests/test_categorizer.py
import pytest
from ml.categorizer import keyword_categorize, bulk_keyword_categorize


def test_keyword_food_detection():
    """Common food merchants correctly categorized."""
    assert keyword_categorize("Swiggy")[0] == "Food"
    assert keyword_categorize("Zomato")[0] == "Food"
    assert keyword_categorize("Dominos")[0] == "Food"


def test_keyword_transport_detection():
    """Common transport merchants correctly categorized."""
    assert keyword_categorize("Uber")[0] == "Transport"
    assert keyword_categorize("Ola")[0] == "Transport"
    assert keyword_categorize("Rapido")[0] == "Transport"


def test_keyword_subscription_detection():
    """Subscription services correctly categorized."""
    assert keyword_categorize("Netflix")[0] == "Subscription"
    assert keyword_categorize("Spotify")[0] == "Subscription"
    assert keyword_categorize("Hotstar")[0] == "Subscription"
    # Amazon Prime is ambiguous due to keyword ordering — test separately
    assert keyword_categorize("Amazon Prime Video")[0] == "Subscription"


def test_keyword_unknown_merchant_returns_other():
    """Unknown merchant falls back to Other with 0.0 confidence."""
    category, confidence = keyword_categorize("XYZ Unknown Shop 9283")
    assert category == "Other"
    assert confidence == 0.0


def test_keyword_confidence_on_match():
    """Matched keywords return confidence of 1.0."""
    _, confidence = keyword_categorize("Swiggy")
    assert confidence == 1.0


def test_bulk_categorize_length():
    """Bulk categorization returns same count as input."""
    merchants = ["Swiggy", "Uber", "Netflix", "Unknown Shop"]
    results = bulk_keyword_categorize(merchants)
    assert len(results) == len(merchants)


def test_bulk_categorize_structure():
    """Each bulk result has required keys."""
    results = bulk_keyword_categorize(["Swiggy"])
    assert "merchant" in results[0]
    assert "category" in results[0]
    assert "confidence" in results[0]
    assert "method" in results[0]


def test_keyword_case_insensitive():
    """Keyword matching works regardless of case."""
    assert keyword_categorize("SWIGGY")[0] == "Food"
    assert keyword_categorize("swiggy")[0] == "Food"
    assert keyword_categorize("Swiggy")[0] == "Food"